from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

GRUPO_ADMIN = 'Administradores'


def es_administrador(user):
    # Puede modificar quien sea staff o pertenezca al grupo Administradores
    if not user.is_authenticated:
        return False
    return (
        user.is_staff
        or user.groups.filter(name=GRUPO_ADMIN).exists()
    )


def solo_administradores(vista):
    # Sin sesión -> redirige al login. Con sesión pero sin permiso -> 403.
    @wraps(vista)
    @login_required(login_url='login')
    def envoltura(request, *args, **kwargs):
        if not es_administrador(request.user):
            raise PermissionDenied
        return vista(request, *args, **kwargs)
    return envoltura
