from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Create user roles (AsistenteGerencia, AdministradorGeneral) and assign permissions.'

    def handle(self, *args, **options):
        # Groups we will create
        groups = {
            'AsistenteGerencia': {
                'description': 'Rol con permisos de gestión (revisar/confirmar/rechazar reservas, bloquear elementos de gestión).',
                'perms': []
            },
            'AdministradorGeneral': {
                'description': 'Rol con todos los permisos administrativos (configurar espacios, precios, agregar socios, etc).',
                'perms': []
            }
        }

        # Build permission lists by app_label/model codenames
        # We will assign fine-grained permissions programmatically below
        from django.apps import apps
        reservas_app = apps.get_app_config('reservas')

        # Helper to fetch permission object safely
        def p(codename):
            try:
                return Permission.objects.get(codename=codename)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Permission not found: {codename}"))
                return None

        # Collect common permissions
        # Reserva: view + change + custom can_confirm/can_reject/can_review (if created)
        reserva_perms = [
            'view_reserva',
            'change_reserva',
            'add_reserva',
            'delete_reserva',
            'can_review_reserva',
            'can_confirm_reserva',
            'can_reject_reserva',
        ]

        # BloqueoEspacio: full management
        bloqueos_perms = [
            'add_bloqueoespacio', 'change_bloqueoespacio', 'delete_bloqueoespacio', 'view_bloqueoespacio'
        ]

        # ConfiguracionSalon: admin should manage prices/params
        configuracion_perms = [
            'add_configuracionsalon', 'change_configuracionsalon', 'delete_configuracionsalon', 'view_configuracionsalon', 'can_modify_prices'
        ]

        # CodigoSocio: only admin general should add/modify socios
        codigosocio_perms = ['add_codigosocio', 'change_codigosocio', 'delete_codigosocio', 'view_codigosocio']

        # ServicioAdicional & ReservaServicioAdicional: admin can manage
        servicio_perms = ['add_servicioadicional','change_servicioadicional','delete_servicioadicional','view_servicioadicional']

        # Auth user: allow assistant to change (block/unblock) users; admin gets full user perms
        auth_user_perms = ['change_user']
        auth_user_admin_perms = ['add_user','change_user','delete_user','view_user']

        # Assign permissions to groups
        # AsistenteGerencia
        asistente_perms = []
        for cod in ['view_reserva','change_reserva','can_review_reserva','can_confirm_reserva','can_reject_reserva']:
            perm = p(cod)
            if perm: asistente_perms.append(perm)
        for cod in bloqueos_perms:
            perm = p(cod)
            if perm: asistente_perms.append(perm)
        # allow assistant to deactivate/block users (change only)
        for cod in auth_user_perms:
            perm = p(cod)
            if perm: asistente_perms.append(perm)

        # AdministradorGeneral: grant all relevant perms in reservas + auth full user perms
        admin_perms = []
        # grab all permissions belonging to the 'reservas' app
        all_reservas_perms = Permission.objects.filter(content_type__app_label='reservas')
        admin_perms.extend(list(all_reservas_perms))
        # add auth user full perms
        for cod in auth_user_admin_perms:
            perm = p(cod)
            if perm: admin_perms.append(perm)

        # Create / update groups
        for name, info in groups.items():
            grp, created = Group.objects.get_or_create(name=name)
            if name == 'AsistenteGerencia':
                grp.permissions.set(asistente_perms)
            else:
                grp.permissions.set(admin_perms)
            grp.save()
            self.stdout.write(self.style.SUCCESS(f"Group '{name}' {'created' if created else 'updated'} with {grp.permissions.count()} permissions."))

        self.stdout.write(self.style.SUCCESS('Roles and permissions setup completed.'))
