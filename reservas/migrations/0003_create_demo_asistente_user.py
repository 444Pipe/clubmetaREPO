from django.db import migrations


def create_demo_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')
    from django.contrib.auth.hashers import make_password

    username = 'asistente_demo'
    email = 'asistente@local'
    raw_password = 'AsistenteDemo2025!'

    # Ensure group exists (created by previous migration or command)
    try:
        group = Group.objects.get(name='AsistenteGerencia')
    except Group.DoesNotExist:
        group = None

    # Create user if not exists
    user, created = User.objects.get_or_create(username=username, defaults={
        'email': email,
        'is_staff': True,
        'is_active': True,
        'password': make_password(raw_password),
    })

    if not created:
        # Ensure staff status and email are set
        changed = False
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_active:
            user.is_active = True
            changed = True
        if user.email != email:
            user.email = email
            changed = True
        if changed:
            user.save()

    # Assign group if available
    if group:
        user.groups.add(group)
        user.save()


def remove_demo_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    try:
        u = User.objects.get(username='asistente_demo')
        u.delete()
    except User.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0002_create_asistente_group'),
    ]

    operations = [
        migrations.RunPython(create_demo_user, remove_demo_user),
    ]
