from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Salon,
    ConfiguracionSalon,
    Reserva,
    CodigoSocio,
    BloqueoEspacio,
    ServicioAdicional,
    ReservaServicioAdicional,
    Comunicado,
    ComunicadoImagen,
)
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

# Register your models here.
from .utils import is_admin_general, is_asistente
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.urls import reverse


# Personalizar la vista de Grupos para añadir una descripción en español
# Esto NO cambia permisos: solo muestra una explicación legible de qué hace cada rol.
try:
    admin.site.unregister(Group)
except Exception:
    pass


class ComunicadoImagenInline(admin.TabularInline):
    model = ComunicadoImagen
    extra = 1
    readonly_fields = ()


@admin.register(Comunicado)
class ComunicadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'publicado', 'activo')
    list_filter = ('activo',)
    search_fields = ('titulo', 'cuerpo')
    inlines = [ComunicadoImagenInline]


class CustomGroupAdmin(DjangoGroupAdmin):
    readonly_fields = ('descripcion_rol',)

    def descripcion_rol(self, obj):
        """Devuelve una descripción en español para los grupos conocidos."""
        if obj is None:
            return ''
        desc_map = {
            'AsistenteGerencia': (
                "Asistente de Gerencia — Puede revisar, confirmar o rechazar "
                "reservas; crear/editar/eliminar bloqueos de espacios; "
                "puede bloquear/desactivar usuarios (NO puede modificar precios, "
                "configuraciones globales ni agregar socios)."
            ),
            'AdministradorGeneral': (
                "Administrador General — Tiene permisos completos: configurar "
                "espacios y montajes; modificar tarifas y parámetros del sistema; "
                "agregar/editar socios; gestionar usuarios. Incluye todos los "
                "permisos del Asistente de Gerencia."
            ),
        }
        return desc_map.get(obj.name, 'Grupo sin descripción específica. Revise los permisos asignados.')

    descripcion_rol.short_description = 'Descripción del rol (español)'

    def get_fieldsets(self, request, obj=None):
        # Insertar el fieldset de descripción antes del fieldset de permisos
        fs = list(super().get_fieldsets(request, obj))
        # Si ya existe un fieldset de descripción, no lo duplicamos
        if not any('Descripción del rol' in str(title) for title, _ in fs):
            fs.insert(1, ('Descripción del rol', {'fields': ('descripcion_rol',)}))
        return fs


admin.site.register(Group, CustomGroupAdmin)


# Personalizar la vista del admin para el modelo User y ocultar el hash
try:
    admin.site.unregister(User)
except Exception:
    pass


class CustomUserAdmin(DjangoUserAdmin):
    """UserAdmin personalizado que no muestra el hash de la contraseña en claro.

    En su lugar muestra un texto amigable en español y un botón para restablecer
    la contraseña (enlace al formulario admin de cambio de contraseña).
    """
    readonly_fields = tuple(getattr(DjangoUserAdmin, 'readonly_fields', ())) + ('password_info',)

    def password_info(self, obj):
        if not obj or not getattr(obj, 'pk', None):
            return ''
        # URL al formulario interno de cambio de contraseña del admin
        try:
            url = reverse('admin:auth_user_password_change', args=[obj.pk])
        except Exception:
            url = '#'
        return format_html(
            '<div>Contraseña: <strong>oculta</strong></div>'
            '<div style="margin-top:6px"><a class="button" href="{}">Restablecer contraseña</a></div>',
            url
        )

    password_info.short_description = 'Contraseña'

    def get_fieldsets(self, request, obj=None):
        """Reemplaza el campo `password` por `password_info` en el primer fieldset."""
        fieldsets = list(super().get_fieldsets(request, obj))
        if fieldsets:
            title, opts = fieldsets[0]
            fields = list(opts.get('fields', ()))
            # Si aparece 'password' lo reemplazamos
            fields = [f if f != 'password' else 'password_info' for f in fields]
            opts = dict(opts)
            opts['fields'] = tuple(fields)
            fieldsets[0] = (title, opts)
        return fieldsets


admin.site.register(User, CustomUserAdmin)

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('disponible',)
    fieldsets = (
        (None, {'fields': ('nombre', 'descripcion', 'imagen', 'disponible')}),
        ('Medidas (metros)', {
            'fields': ('largo_m', 'ancho_m', 'alto_m', 'diametro_m')
        }),
        ('Tarima (opcional, metros)', {
            'fields': ('tarima_largo_m', 'tarima_ancho_m', 'tarima_alto_m')
        }),
    )


class ConfiguracionSalonInline(admin.TabularInline):
    model = ConfiguracionSalon
    extra = 1
    fields = ('tipo_configuracion', 'capacidad', 'imagen_montaje', 'precio_socio_4h', 'precio_particular_4h', 'precio_socio_8h', 'precio_particular_8h')


@admin.register(ConfiguracionSalon)
class ConfiguracionSalonAdmin(admin.ModelAdmin):
    list_display = ('salon', 'tipo_configuracion', 'capacidad', 'precio_socio_4h_display', 'precio_particular_4h_display')
    list_filter = ('salon', 'tipo_configuracion')
    search_fields = ('salon__nombre',)
    fieldsets = (
        ('Información General', {
            'fields': ('salon', 'tipo_configuracion', 'capacidad', 'imagen_montaje')
        }),
        ('Precios para Socios', {
            'fields': ('precio_socio_4h', 'precio_socio_8h')
        }),
        ('Precios para Particulares', {
            'fields': ('precio_particular_4h', 'precio_particular_8h')
        }),
    )

    def precio_socio_4h_display(self, obj):
        return money_format(obj.precio_socio_4h)
    precio_socio_4h_display.short_description = 'Precio socio (4h)'
    precio_socio_4h_display.admin_order_field = 'precio_socio_4h'

    def precio_particular_4h_display(self, obj):
        return money_format(obj.precio_particular_4h)
    precio_particular_4h_display.short_description = 'Precio particular (4h)'
    precio_particular_4h_display.admin_order_field = 'precio_particular_4h'

    actions = ['cambiar_precios_seleccionados']

    class SalonPriceChangeForm(forms.Form):
        FIELD_CHOICES = (
            ('precio_socio_4h', 'Precio socio (4h)'),
            ('precio_particular_4h', 'Precio particular (4h)'),
            ('precio_socio_8h', 'Precio socio (8h)'),
            ('precio_particular_8h', 'Precio particular (8h)'),
        )
        field_name = forms.ChoiceField(choices=FIELD_CHOICES, label='Campo a modificar')
        precio = forms.CharField(label='Nuevo precio', required=True, widget=forms.TextInput(attrs={'inputmode': 'numeric'}))

    def cambiar_precios_seleccionados(self, request, queryset):
        """Admin action to set a given price field for selected salon configurations."""
        if 'apply' in request.POST:
            form = self.SalonPriceChangeForm(request.POST)
            if form.is_valid():
                field_name = form.cleaned_data['field_name']
                raw_price = form.cleaned_data['precio']
                try:
                    dec = parse_price_input(raw_price)
                except ValidationError as e:
                    self.message_user(request, f'Error: {e.message}', level=messages.ERROR)
                    return None

                # Use update to set the chosen field
                update_kwargs = {field_name: dec}
                count = queryset.update(**update_kwargs)
                self.message_user(request, f'{count} configuración(es) actualizada(s).', level=messages.SUCCESS)
                return None
        else:
            form = self.SalonPriceChangeForm()

        context = {
            'objects': queryset,
            'form': form,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
            'queryset_count': queryset.count(),
        }
        return render(request, 'admin/reservas/configuracionsalon/change_price_action.html', context)

    cambiar_precios_seleccionados.short_description = 'Cambiar precios de las configuraciones seleccionadas'

    # -----------------------
    # Role-based permission guards
    # -----------------------
    def has_change_permission(self, request, obj=None):
        # Only AdministradorGeneral (or superuser) can change configurations/prices
        return is_admin_general(request.user)

    def has_add_permission(self, request):
        return is_admin_general(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_admin_general(request.user)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not is_admin_general(request.user):
            # remove price-change action for non-admins
            actions.pop('cambiar_precios_seleccionados', None)
        return actions


@admin.register(CodigoSocio)
class CodigoSocioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre_socio', 'identificacion', 'email', 'celular', 'empresa', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre_socio', 'identificacion', 'email', 'celular', 'empresa')
    list_editable = ('activo',)
    readonly_fields = ('fecha_creacion',)
    fieldsets = (
        ('Información del Socio', {
            'fields': ('codigo', 'nombre_socio', 'identificacion', 'email', 'celular', 'empresa', 'activo')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Only AdministradorGeneral may add new socios
        return is_admin_general(request.user)

    def has_change_permission(self, request, obj=None):
        # Only AdministradorGeneral may modify socio records via admin
        return is_admin_general(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_admin_general(request.user)


class SocioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('nombre', 'email', 'telefono')
    actions = ['enviar_notificacion_manual']

    def enviar_notificacion_manual(self, request, queryset):
        """Enviar notificación por email y registrar en EmailLog. Contenido por defecto; puede personalizarse"""
        # import signals locally to avoid circular imports during admin module import
        from . import signals as signals_module
        subject = 'Notificación desde Club El Meta'
        for socio in queryset:
            # enviar email
            try:
                # render synchronously for logging, send async to avoid blocking
                txt, html = signals_module._render_message(
                    subject,
                    'reservas/emails/admin_manual_notification.txt',
                    'reservas/emails/admin_manual_notification.html',
                    {'socio': socio}
                )
                try:
                    from reservas.utils.email_async import send_email_async
                    send_email_async(
                        subject=subject,
                        template_txt='reservas/emails/admin_manual_notification.txt',
                        template_html='reservas/emails/admin_manual_notification.html',
                        context={'socio': socio},
                        recipient_list=[socio.email]
                    )
                    success, error = True, None
                except Exception:
                    success, error = False, 'async send failed'
                try:
                    EmailLog.objects.create(
                        reserva=None,
                        channel='EMAIL',
                        to_email=socio.email,
                        subject=subject,
                        body_text=txt,
                        body_html=html,
                        success=bool(success),
                        error=error if error else None,
                    )
                except Exception:
                    pass
            except Exception:
                pass
        self.message_user(request, f'Notificaciones enviadas a {queryset.count()} socio(s) (intentos registrados en EmailLog).')
    enviar_notificacion_manual.short_description = 'Enviar notificación manual (email)'


class ReservaServicioAdicionalInline(admin.TabularInline):
    model = ReservaServicioAdicional
    extra = 1
    fields = ('servicio', 'cantidad', 'precio_unitario', 'subtotal_display', 'notas')
    readonly_fields = ('subtotal_display',)

    def subtotal_display(self, obj):
        return money_format(obj.subtotal)
    subtotal_display.short_description = 'Subtotal'


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('configuracion_salon', 'nombre_cliente', 'fecha_evento', 'tipo_cliente', 'duracion', 'numero_personas', 'precio_total_display', 'estado')
    list_filter = ('estado', 'tipo_cliente', 'duracion', 'fecha_evento')
    search_fields = ('nombre_cliente', 'email_cliente', 'telefono_cliente', 'configuracion_salon__salon__nombre')
    list_editable = ('estado',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    date_hierarchy = 'fecha_evento'
    inlines = [ReservaServicioAdicionalInline]
    
    fieldsets = (
        ('Información del Salón', {
            'fields': ('configuracion_salon', 'fecha_evento', 'duracion', 'numero_personas')
        }),
        ('Información del Cliente', {
            'fields': ('nombre_cliente', 'email_cliente', 'telefono_cliente', 'tipo_cliente')
        }),
        ('Precio y Estado', {
            'fields': ('precio_total', 'estado')
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )

    def precio_total_display(self, obj):
        return money_format(obj.precio_total)
    precio_total_display.short_description = 'Precio total'
    precio_total_display.admin_order_field = 'precio_total'

    # Make most fields readonly for AsistenteGerencia; allow them only to edit reservation state and observations.
    def get_readonly_fields(self, request, obj=None):
        if is_asistente(request.user) and not is_admin_general(request.user):
            editable = set(['estado', 'observaciones'])
            all_fields = [f.name for f in self.model._meta.fields]
            readonly = [f for f in all_fields if f not in editable]
            base = list(super().get_readonly_fields(request, obj) or [])
            return list(set(base + readonly))
        return super().get_readonly_fields(request, obj)


@admin.register(BloqueoEspacio)
class BloqueoEspacioAdmin(admin.ModelAdmin):
    list_display = ('salon', 'rango_fechas', 'motivo_badge', 'activo_badge', 'fecha_creacion')
    list_filter = ('activo', 'motivo', 'salon')
    search_fields = ('salon__nombre', 'descripcion')
    readonly_fields = ('fecha_creacion',)
    date_hierarchy = 'fecha_inicio'
    actions = ['delete_selected', 'eliminar_bloqueos']
    list_display_links = ('salon', 'rango_fechas')

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }
    
    def eliminar_bloqueos(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} bloqueo(s) eliminado(s) exitosamente.')
    eliminar_bloqueos.short_description = "🗑️ Eliminar bloqueos seleccionados"
    
    # Use a custom form with HTML5 time inputs so admins can set exact hours:minutes
    class BloqueoForm(forms.ModelForm):
        class Meta:
            model = BloqueoEspacio
            fields = '__all__'
            widgets = {
                'hora_inicio': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
                'hora_fin': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            }

    form = BloqueoForm

    fieldsets = (
        ('Información del Bloqueo', {
            'fields': ('salon', 'fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin', 'activo')
        }),
        ('Detalles', {
            'fields': ('motivo', 'descripcion')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )

    def rango_fechas(self, obj):
        if obj.fecha_inicio and obj.fecha_fin:
            inicio = obj.fecha_inicio.strftime('%d %b %Y')
            fin = obj.fecha_fin.strftime('%d %b %Y')
            if obj.hora_inicio or obj.hora_fin:
                hi = obj.hora_inicio.strftime('%H:%M') if obj.hora_inicio else '--:--'
                hf = obj.hora_fin.strftime('%H:%M') if obj.hora_fin else '--:--'
                return format_html('<strong>{} {}</strong> → <small style="color:#6b7280">{} {}</small>', inicio, hi, fin, hf)
            return format_html('<strong>{}</strong> → <small style="color:#6b7280">{}</small>', inicio, fin)
        if obj.fecha_inicio:
            return obj.fecha_inicio.strftime('%d %b %Y')
        return '-'
    rango_fechas.short_description = 'Rango'
    rango_fechas.admin_order_field = 'fecha_inicio'

    def motivo_badge(self, obj):
        label = obj.motivo or 'Otro'
        color = {
            'Mantenimiento': '#f97316',
            'Evento Privado': '#06b6d4',
            'Reparación': '#ef4444',
            'Otro': '#6b7280'
        }.get(label, '#6b7280')
        return format_html('<span style="background:{}; color: white; padding:4px 8px; border-radius:12px; font-size:0.85rem;">{}</span>', color, label)
    motivo_badge.short_description = 'Motivo'

    def activo_badge(self, obj):
        if obj.activo:
            return format_html('<span style="background:#10b981; color:white; padding:4px 8px; border-radius:12px; font-size:0.85rem;">{}</span>', 'Sí')
        return format_html('<span style="background:#6b7280; color:white; padding:4px 8px; border-radius:12px; font-size:0.85rem;">{}</span>', 'No')
    activo_badge.short_description = 'Activo'


def parse_price_input(raw):
    """Parse a human-friendly price string into a Decimal with 2 decimals.

    Accepts formats like: '3k', '2.5k', '1m', '30,000', '3.000', '3.000,50', '3,000.50'.
    Raises `ValidationError` on parse failure.
    """
    if raw is None:
        raise ValidationError('Precio unitario es requerido.')
    s = str(raw).strip().lower()
    if s == '':
        raise ValidationError('Precio unitario es requerido.')

    m = re.match(r'^([0-9.,]+)\s*([km])?$', s)
    if m:
        number_part = m.group(1)
        suffix = m.group(2)
        try:
            # Normalize separators first
            if '.' in number_part and ',' in number_part:
                number_part = number_part.replace('.', '').replace(',', '.')
            elif number_part.count(',') == 1 and number_part.count('.') == 0 and len(number_part.split(',')[1]) <= 2:
                number_part = number_part.replace(',', '.')
            elif number_part.count('.') > 1:
                number_part = number_part.replace('.', '')
            elif number_part.count('.') == 1 and len(number_part.split('.')[1]) == 3:
                # treat single dot with 3 digits after as thousands separator
                number_part = number_part.replace('.', '')
            else:
                number_part = number_part.replace(',', '')

            val = float(number_part)
            if suffix == 'k':
                val = val * 1000
            elif suffix == 'm':
                val = val * 1000000
            dec = Decimal(str(val)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return dec
        except (ValueError, InvalidOperation):
            raise ValidationError('Formato de precio no reconocido.')

    # Fallback: try generic normalization
    try:
        if '.' in s and ',' in s:
            s = s.replace('.', '').replace(',', '.')
        elif ',' in s and '.' not in s:
            # If comma present and looks like decimal part (<=2 digits), treat as decimal
            parts = s.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                s = s.replace(',', '.')
            else:
                s = s.replace(',', '')
        elif s.count('.') > 1:
            s = s.replace('.', '')

        dec = Decimal(s)
        dec = dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return dec
    except (InvalidOperation, ValueError):
        raise ValidationError('Formato de precio no reconocido.')


class ServicioAdicionalForm(forms.ModelForm):
    class Meta:
        model = ServicioAdicional
        fields = '__all__'
        widgets = {
            'precio_unitario': forms.TextInput(attrs={'inputmode': 'numeric'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace the default DecimalField form field with a CharField so we
        # receive the raw input string and can normalize it server-side.
        if 'precio_unitario' in self.fields:
            self.fields['precio_unitario'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'inputmode': 'numeric'}))

    def clean_precio_unitario(self):
        raw = self.cleaned_data.get('precio_unitario')
        try:
            return parse_price_input(raw)
        except ValidationError as e:
            raise forms.ValidationError(e.message)


class PriceChangeForm(forms.Form):
    precio = forms.CharField(label='Nuevo precio', required=True, widget=forms.TextInput(attrs={'inputmode': 'numeric'}))


@admin.register(ServicioAdicional)
class ServicioAdicionalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_unitario_display', 'unidad_medida', 'activo')
    list_filter = ('activo', 'unidad_medida')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)
    
    fieldsets = (
        ('Información del Servicio', {
            'fields': ('nombre', 'descripcion', 'activo')
        }),
        ('Precio', {
            'fields': ('precio_unitario', 'unidad_medida')
        }),
    )

    class Media:
        js = ('js/admin_price_format.js',)

    # Use the ModelForm that normalizes human-friendly price input server-side
    form = ServicioAdicionalForm

    actions = ['cambiar_precio_seleccionados']

    def cambiar_precio_seleccionados(self, request, queryset):
        """Admin action to set a new `precio_unitario` for selected servicios.

        Shows a small form to enter the new price and applies it to the selection.
        """
        if 'apply' in request.POST:
            form = PriceChangeForm(request.POST)
            if form.is_valid():
                raw_price = form.cleaned_data['precio']
                try:
                    dec = parse_price_input(raw_price)
                except ValidationError as e:
                    self.message_user(request, f'Error: {e.message}', level=messages.ERROR)
                    return None

                count = queryset.update(precio_unitario=dec)
                self.message_user(request, f'{count} servicio(s) actualizado(s) con el nuevo precio {dec}.')
                return None
        else:
            form = PriceChangeForm()

        # Render a simple confirmation form
        context = {
            'servicios': queryset,
            'form': form,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
            'queryset_count': queryset.count(),
        }
        return render(request, 'admin/reservas/servicioadicional/change_price_action.html', context)

    cambiar_precio_seleccionados.short_description = 'Cambiar precio de los servicios seleccionados'

    # Provide a small help text so admins understand accepted formats
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'precio_unitario' in form.base_fields:
            form.base_fields['precio_unitario'].help_text = (
                'Formato aceptado: puede usar `3k` → 3.000, `30,000` o `30.000` para treinta mil, ' 
                'o escribir decimales como `3.000,50`. En el formulario se normaliza automáticamente.'
            )
        return form

    def precio_unitario_display(self, obj):
        return money_format(obj.precio_unitario)
    precio_unitario_display.short_description = 'Precio unitario'
    precio_unitario_display.admin_order_field = 'precio_unitario'


def money_format(value):
    if value is None:
        return '-'
    try:
        return format_html("{}", f"${value:,.2f}")
    except Exception:
        return format_html("{}", value)


try:
    from .models import EmailLog

    @admin.register(EmailLog)
    class EmailLogAdmin(admin.ModelAdmin):
        from django.contrib import messages
        from django.utils.translation import gettext_lazy as _

        list_display = ('created_at', 'get_target', 'channel', 'success')
        list_filter = ('channel', 'success')
        search_fields = ('to_email', 'subject', 'error')
        readonly_fields = ('reserva', 'channel', 'to_email', 'subject', 'body_text', 'body_html', 'success', 'error', 'created_at')
        ordering = ('-created_at',)
        actions = []

        def get_target(self, obj):
            return obj.to_email or 'sin destino'
        get_target.short_description = 'Destino'

        def changelist_view(self, request, extra_context=None):
            """Wrap the changelist view to log unexpected exceptions and show a friendly admin message instead of a raw 500."""
            import logging
            import traceback as _traceback
            from django.http import HttpResponse
            try:
                return super().changelist_view(request, extra_context=extra_context)
            except Exception as e:
                logging.getLogger(__name__).error('Error mostrando EmailLog changelist: %s\n%s', str(e), _traceback.format_exc())
                try:
                    self.message_user(request, 'Error mostrando registros de EmailLog. Revise los logs del servidor.', level=messages.ERROR)
                except Exception:
                    pass
                return HttpResponse('Error interno procesando la vista. Revise los logs.', status=500)

        # The 'reenviar_seleccionados' action was intentionally removed to prevent accidental re-sends from admin.
except Exception:
    # EmailLog model may not be available during some import sequences; skip admin registration if so
    pass

# Register Socio admin if model is available (guard against import-time cycles)
try:
    from .models import Socio
    admin.site.register(Socio, SocioAdmin)
except Exception:
    pass

# ManualNotification model removed; no admin UI for manual WhatsApp/email sends.

