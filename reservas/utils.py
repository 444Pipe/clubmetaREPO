from django.core.exceptions import PermissionDenied


def user_in_group(user, group_name):
    """Return True if user belongs to group `group_name`.

    Helper used across admin and views. Does not treat superuser specially
    (so checks later can allow superuser as needed).
    """
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


def is_admin_general(user):
    """True if the user is superuser or member of AdministradorGeneral group."""
    return bool(user and (user.is_superuser or user_in_group(user, 'AdministradorGeneral')))


def is_asistente(user):
    """True if the user is member of AsistenteGerencia group."""
    return bool(user and user_in_group(user, 'AsistenteGerencia'))


def require_admin_general(user):
    """Raise PermissionDenied if user is not admin general."""
    if not is_admin_general(user):
        raise PermissionDenied("Se requieren privilegios de Administrador General.")


def require_asistente_or_admin(user):
    """Raise PermissionDenied unless user is assistant or admin general."""
    if not (is_asistente(user) or is_admin_general(user)):
        raise PermissionDenied("Se requieren privilegios de Asistente de Gerencia o Administrador General.")
