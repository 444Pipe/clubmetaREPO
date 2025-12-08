from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Salon, ConfiguracionSalon, Reserva, CodigoSocio, BloqueoEspacio, Beneficio, Socio

# Register your models here.

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('disponible',)


class ConfiguracionSalonInline(admin.TabularInline):
    model = ConfiguracionSalon
    extra = 1
    fields = ('tipo_configuracion', 'capacidad', 'precio_socio_4h', 'precio_particular_4h', 'precio_socio_8h', 'precio_particular_8h')


@admin.register(ConfiguracionSalon)
class ConfiguracionSalonAdmin(admin.ModelAdmin):
    list_display = ('salon', 'tipo_configuracion', 'capacidad', 'precio_socio_4h_display', 'precio_particular_4h_display')
    list_filter = ('salon', 'tipo_configuracion')
    search_fields = ('salon__nombre',)
    fieldsets = (
        ('Información General', {
            'fields': ('salon', 'tipo_configuracion', 'capacidad')
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


@admin.register(CodigoSocio)
class CodigoSocioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre_socio', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre_socio')
    list_editable = ('activo',)
    readonly_fields = ('fecha_creacion',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('configuracion_salon', 'nombre_cliente', 'fecha_evento', 'tipo_cliente', 'duracion', 'numero_personas', 'precio_total_display', 'estado')
    list_filter = ('estado', 'tipo_cliente', 'duracion', 'fecha_evento')
    search_fields = ('nombre_cliente', 'email_cliente', 'telefono_cliente', 'configuracion_salon__salon__nombre')
    list_editable = ('estado',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    date_hierarchy = 'fecha_evento'
    
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
                if getattr(obj, 'hora_inicio', None) or getattr(obj, 'hora_fin', None):
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
            return format_html('<span style="background:#10b981; color:white; padding:4px 8px; border-radius:12px; font-size:0.85rem;">Sí</span>')
        return format_html('<span style="background:#6b7280; color:white; padding:4px 8px; border-radius:12px; font-size:0.85rem;">No</span>')
    activo_badge.short_description = 'Activo'


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'email', 'telefono', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('nombre', 'email', 'telefono', 'codigo__codigo')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    filter_horizontal = ('beneficios',)
    fieldsets = (
        ('Información personal', {
            'fields': ('user', 'codigo', 'nombre', 'email', 'telefono', 'direccion')
        }),
        ('Estado y Beneficios', {
            'fields': ('estado', 'beneficios', 'notas')
        }),
        ('Tiempos', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )


def money_format(value):
    if value is None:
        return '-'
    try:
        return format_html("{}", f"${value:,.2f}")
    except Exception:
        return format_html("{}", value)

