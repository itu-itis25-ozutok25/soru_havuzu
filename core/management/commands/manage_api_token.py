from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from rest_framework.authtoken.models import Token

from core.api_permissions import API_GROUPS, API_SERVER_GROUP, API_STUDENT_GROUP


ROLE_TO_GROUP = {
    "student": API_STUDENT_GROUP,
    "server": API_SERVER_GROUP,
}


class Command(BaseCommand):
    help = "Entegrasyon kullanıcısının API tokenını oluşturur, yeniler veya iptal eder."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Her tüketici uygulama için benzersiz kullanıcı adı")
        parser.add_argument("--role", choices=ROLE_TO_GROUP, help="Tokenın API rolü")
        parser.add_argument(
            "--rotate",
            action="store_true",
            help="Mevcut tokenı iptal edip yeni bir token üretir",
        )
        parser.add_argument(
            "--revoke",
            action="store_true",
            help="Mevcut tokenı iptal eder",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"].strip()
        if not username:
            raise CommandError("Kullanıcı adı boş olamaz.")
        if options["revoke"] and options["rotate"]:
            raise CommandError("--revoke ve --rotate birlikte kullanılamaz.")

        user_model = get_user_model()
        if options["revoke"]:
            try:
                user = user_model.objects.get(username=username)
            except user_model.DoesNotExist as exc:
                raise CommandError("Entegrasyon kullanıcısı bulunamadı.") from exc
            deleted, _ = Token.objects.filter(user=user).delete()
            if not deleted:
                raise CommandError("Bu kullanıcı için aktif token bulunamadı.")
            self.stdout.write(self.style.SUCCESS(f"Token iptal edildi: {username}"))
            return

        role = options["role"]
        if not role:
            raise CommandError("Token oluşturmak için --role student veya --role server gereklidir.")

        user, created = user_model.objects.get_or_create(username=username)
        if created:
            user.set_unusable_password()
            user.is_staff = False
            user.is_superuser = False
            user.save(update_fields=("password", "is_staff", "is_superuser"))
        elif user.has_usable_password() or user.is_staff or user.is_superuser:
            raise CommandError(
                "İnsan/yönetici hesabına API tokenı atanamaz. Ayrı bir entegrasyon kullanıcı adı seçin."
            )
        if not user.is_active:
            raise CommandError("Pasif kullanıcı için token oluşturulamaz.")

        groups = {group.name: group for group in Group.objects.filter(name__in=API_GROUPS)}
        missing_groups = set(API_GROUPS) - set(groups)
        if missing_groups:
            raise CommandError("API rol grupları eksik. Önce migrationları çalıştırın.")

        user.groups.remove(*groups.values())
        user.groups.add(groups[ROLE_TO_GROUP[role]])

        existing_token = Token.objects.filter(user=user).first()
        if existing_token and not options["rotate"]:
            raise CommandError("Bu kullanıcıda token var. Yenilemek için --rotate kullanın.")
        if existing_token:
            existing_token.delete()

        token = Token.objects.create(user=user)
        action = "yenilendi" if options["rotate"] else "oluşturuldu"
        self.stdout.write(self.style.SUCCESS(f"Token {action}: {username} ({role})"))
        self.stdout.write(token.key)
        self.stdout.write("Bu değer yalnızca güvenli bir sır deposunda saklanmalıdır.")
