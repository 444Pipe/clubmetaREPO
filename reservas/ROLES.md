Resumen del sistema de Roles (Asistente de Gerencia / Administrador General)

Objetivo
--------
Implementar dos roles con permisos claros y limitados:

1. Asistente de Gerencia
   - Puede revisar, confirmar o rechazar reservas.
   - Puede bloquear usuarios (modificar `is_active` en Django User mediante `change_user`).
   - Puede gestionar bloqueos de espacios (`BloqueoEspacio`).
   - No puede modificar configuraciones globales, precios ni agregar socios.

2. Administrador General
   - Tiene permisos completos sobre modelos relevantes: `ConfiguracionSalon`, `CodigoSocio`, `Reserva`, `BloqueoEspacio`, `ServicioAdicional`.
   - Puede modificar precios, parámetros del sistema y agregar socios.
   - Incluye los permisos de Asistente de Gerencia.

Código implementado
--------------------
- `reservas/models.py`
  - Añade permisos custom a `Reserva` (`can_review_reserva`, `can_confirm_reserva`, `can_reject_reserva`).
  - Añade permiso `can_modify_prices` a `ConfiguracionSalon`.

- `reservas/utils.py`
  - Contiene helpers: `is_admin_general`, `is_asistente`, `require_admin_general`, `require_asistente_or_admin`.
  - Usados por admin y vistas para verificar roles.

- `reservas/management/commands/setup_roles.py`
  - Comando para crear/actualizar los grupos `AsistenteGerencia` y `AdministradorGeneral` y asignar permisos apropiados.
  - Ejecutar: `python manage.py setup_roles`

- `reservas/admin.py` (ajustes)
  - Importa `is_admin_general`, `is_asistente`.
  - `ConfiguracionSalonAdmin` restringe añadir/editar/eliminar y quita la acción de cambio de precios a no-admins.
  - `CodigoSocioAdmin` restringe añadir/editar/eliminar a Administrador General.
  - `ReservaAdmin` hace readonly la mayoría de campos para asistentes; solo `estado` y `observaciones` editables.

- `reservas/views.py` (ajuste)
  - Vista `admin` verifica permisos finos antes de permitir cambios rápidos de estado en las reservas.

Pasos de despliegue
-------------------
1. Crear migración para aplicar los nuevos permisos definidos en los `Meta.permissions` y ejecutar migraciones:

```powershell
python manage.py makemigrations reservas
python manage.py migrate
```

2. Ejecutar el comando que crea los grupos y asigna permisos:

```powershell
python manage.py setup_roles
```

3. Crear/actualizar cuentas de usuario en el admin y asignarles el grupo `AsistenteGerencia` o `AdministradorGeneral`.

Notas y consideraciones
-----------------------
- El comando `setup_roles` asigna permisos basándose en los `codename` existentes. Si alguna perm no existe (por ejemplo, antes de ejecutar migraciones), el comando mostrará una advertencia.
- Se recomienda revisar los permisos en el admin (`/admin/auth/group/`) después de ejecutar el comando.
- Los cambios en `admin.py` usan comprobaciones por grupo; los superusers conservan todos los privilegios por diseño.
- Si deseas una política más estricta (p. ej. asistentes no pueden ver ciertos objetos en admin), podemos añadir `get_queryset` filtrado por usuario.

Si quieres que aplique restricciones adicionales (p. ej. que los asistentes solo vean reservas de ciertos salones) puedo implementarlo también.
