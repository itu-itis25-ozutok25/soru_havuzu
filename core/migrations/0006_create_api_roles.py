from django.db import migrations


API_GROUPS = ("api_student", "api_server")


def create_api_groups(apps, schema_editor):
    group_model = apps.get_model("auth", "Group")
    for group_name in API_GROUPS:
        group_model.objects.get_or_create(name=group_name)


def remove_api_groups(apps, schema_editor):
    group_model = apps.get_model("auth", "Group")
    group_model.objects.filter(name__in=API_GROUPS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("core", "0005_question_archived_at_question_image_hash"),
    ]

    operations = [
        migrations.RunPython(create_api_groups, remove_api_groups),
    ]
