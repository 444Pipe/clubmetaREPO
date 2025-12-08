from django.db import migrations


def create_asistente_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group, created = Group.objects.get_or_create(name='AsistenteGerencia')

    # codenames we try to assign (some may not exist yet depending on migration order)
    codenames = [
        'view_reserva', 'change_reserva', 'can_review_reserva', 'can_confirm_reserva', 'can_reject_reserva',
        'add_bloqueoespacio', 'change_bloqueoespacio', 'delete_bloqueoespacio', 'view_bloqueoespacio',
        'change_user',
    ]

    perms = list(Permission.objects.filter(codename__in=codenames))
    if perms:
        group.permissions.set(perms)
        group.save()


def remove_asistente_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    try:
        g = Group.objects.get(name='AsistenteGerencia')
        g.delete()
    except Group.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_asistente_group, remove_asistente_group),
    ]
