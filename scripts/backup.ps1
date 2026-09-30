[CmdletBinding()]
param(
    [string]$OutputRoot = "backups",
    [string]$ComposeFile = "docker-compose.yml"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$composePath = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $ComposeFile))
if (-not (Test-Path -LiteralPath $composePath -PathType Leaf)) {
    throw "Compose dosyası bulunamadı: $composePath"
}

$outputPath = if ([System.IO.Path]::IsPathRooted($OutputRoot)) {
    [System.IO.Path]::GetFullPath($OutputRoot)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $projectRoot $OutputRoot))
}
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupPath = Join-Path $outputPath $timestamp
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

$composeArgs = @("compose", "-f", $composePath)
$databaseContainer = (& docker @composeArgs ps -q db).Trim()
$webContainer = (& docker @composeArgs ps -q web).Trim()
if (-not $databaseContainer -or -not $webContainer) {
    throw "db ve web servisleri çalışıyor olmalıdır."
}

& docker @composeArgs exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/soru_havuzu.dump'
if ($LASTEXITCODE -ne 0) { throw "Veritabanı yedeği alınamadı." }
& docker cp "${databaseContainer}:/tmp/soru_havuzu.dump" (Join-Path $backupPath "database.dump")
& docker @composeArgs exec -T db rm -f /tmp/soru_havuzu.dump

& docker @composeArgs exec -T web sh -c 'mkdir -p /app/media && tar -czf /tmp/soru_havuzu-media.tar.gz -C /app media'
if ($LASTEXITCODE -ne 0) { throw "Medya yedeği alınamadı." }
& docker cp "${webContainer}:/tmp/soru_havuzu-media.tar.gz" (Join-Path $backupPath "media.tar.gz")
& docker @composeArgs exec -T web rm -f /tmp/soru_havuzu-media.tar.gz

$manifest = [ordered]@{
    createdAt = (Get-Date).ToUniversalTime().ToString("o")
    databaseSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $backupPath "database.dump")).Hash
    mediaSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $backupPath "media.tar.gz")).Hash
}
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $backupPath "manifest.json") -Encoding UTF8

Write-Host "Yedek oluşturuldu: $backupPath"
