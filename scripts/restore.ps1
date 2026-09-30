[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "High")]
param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath,
    [string]$ComposeFile = "docker-compose.yml"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$resolvedBackup = (Resolve-Path -LiteralPath $BackupPath).Path
$composePath = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $ComposeFile))
$databaseDump = Join-Path $resolvedBackup "database.dump"
$mediaArchive = Join-Path $resolvedBackup "media.tar.gz"
$manifestPath = Join-Path $resolvedBackup "manifest.json"

foreach ($requiredFile in @($composePath, $databaseDump, $mediaArchive, $manifestPath)) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Gerekli dosya bulunamadı: $requiredFile"
    }
}

$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
$databaseHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $databaseDump).Hash
$mediaHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $mediaArchive).Hash
if ($databaseHash -ne $manifest.databaseSha256 -or $mediaHash -ne $manifest.mediaSha256) {
    throw "Yedek bütünlük kontrolü başarısız oldu."
}

if (-not $PSCmdlet.ShouldProcess(
    "Veritabanı ve medya içeriği",
    "Seçilen yedekten geri yükle"
)) {
    return
}

$composeArgs = @("compose", "-f", $composePath)
$databaseContainer = (& docker @composeArgs ps -q db).Trim()
if (-not $databaseContainer) {
    throw "db servisi çalışıyor olmalıdır."
}

& docker @composeArgs stop web
try {
    & docker cp $databaseDump "${databaseContainer}:/tmp/soru_havuzu-restore.dump"
    & docker @composeArgs exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner /tmp/soru_havuzu-restore.dump'
    if ($LASTEXITCODE -ne 0) { throw "Veritabanı geri yüklenemedi." }
    & docker @composeArgs exec -T db rm -f /tmp/soru_havuzu-restore.dump

    & docker @composeArgs run --rm --no-deps -v "${resolvedBackup}:/restore:ro" web sh -c 'find /app/media -mindepth 1 -maxdepth 1 -exec rm -rf -- {} + && tar -xzf /restore/media.tar.gz -C /app'
    if ($LASTEXITCODE -ne 0) { throw "Medya dosyaları geri yüklenemedi." }
}
finally {
    & docker @composeArgs up -d web
}

Write-Host "Geri yükleme tamamlandı: $resolvedBackup"
