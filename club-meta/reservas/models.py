from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

class Salon(models.Model):
    """Modelo para representar los salones del club"""
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, help_text="Descripción del salón")
    imagen = models.CharField(max_length=200, blank=True, help_text="Ruta de la imagen del salón")
    disponible = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Salón"
        verbose_name_plural = "Salones"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class ConfiguracionSalon(models.Model):
    """Modelo para las diferentes configuraciones/montajes de un salón"""
    
    TIPO_CONFIGURACION_CHOICES = [
        ('MESA_U', 'Mesa en U'),
        ('AUDITORIO', 'Auditorio'),
        ('ESCUELA', 'Escuela'),
        ('BANQUETE', 'Banquete'),
        ('SOFA', 'Sofá'),
        ('CORTESIA', 'Cortesía'),
        ('MESA_12', 'Mesa de 12'),
        ('IMPERIAL', 'Imperial'),
        ('EMPRESARIAL', 'Empresarial'),
    ]
    
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='configuraciones')
    tipo_configuracion = models.CharField(max_length=20, choices=TIPO_CONFIGURACION_CHOICES)
    capacidad = models.IntegerField(validators=[MinValueValidator(1)], help_text="Capacidad máxima en esta configuración")
    
    # Precios para socios
    precio_socio_4h = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio para socios (4 horas)")
    precio_socio_8h = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Precio para socios (8 horas)")
    
    # Precios para particulares
    precio_particular_4h = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio para particulares (4 horas)")
    precio_particular_8h = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Precio para particulares (8 horas)")
    
    class Meta:
        verbose_name = "Configuración de Salón"
        verbose_name_plural = "Configuraciones de Salones"
        ordering = ['salon__nombre', 'tipo_configuracion']
        unique_together = ['salon', 'tipo_configuracion']
    
    def __str__(self):
        return f"{self.salon.nombre} - {self.get_tipo_configuracion_display()} ({self.capacidad} PAX)"


class Reserva(models.Model):
    """Modelo para gestionar las reservas de salones"""
    
    TIPO_CLIENTE_CHOICES = [
        ('SOCIO', 'Socio'),
        ('PARTICULAR', 'Particular'),
    ]
    
    DURACION_CHOICES = [
        ('4H', '4 Horas'),
        ('8H', '8 Horas'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('COMPLETADA', 'Completada'),
    ]
    
    configuracion_salon = models.ForeignKey('ConfiguracionSalon', on_delete=models.CASCADE, related_name='reservas')
    
    # Información del cliente
    nombre_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=20)
    tipo_cliente = models.CharField(max_length=20, choices=TIPO_CLIENTE_CHOICES, default='PARTICULAR')
    nombre_entidad = models.CharField(max_length=200, blank=True, null=True)  # Empresa/Entidad del cliente
    
    # Detalles de la reserva
    fecha_evento = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)  # Hora de inicio del evento
    duracion = models.CharField(max_length=2, choices=DURACION_CHOICES, default='4H')
    tiempo_decoracion = models.IntegerField(default=0, validators=[MinValueValidator(0)])  # Horas adicionales para decoración
    numero_personas = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Precio y estado
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    
    # Información adicional
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_evento', '-fecha_creacion']
    
    def __str__(self):
        return f"{self.configuracion_salon.salon.nombre} - {self.nombre_cliente} - {self.fecha_evento}"
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente el precio según el tipo de cliente y duración"""
        if not self.precio_total or self.precio_total == 0:
            if self.tipo_cliente == 'SOCIO':
                if self.duracion == '4H':
                    self.precio_total = self.configuracion_salon.precio_socio_4h
                else:
                    self.precio_total = self.configuracion_salon.precio_socio_8h or self.configuracion_salon.precio_socio_4h
            else:  # PARTICULAR
                if self.duracion == '4H':
                    self.precio_total = self.configuracion_salon.precio_particular_4h
                else:
                    self.precio_total = self.configuracion_salon.precio_particular_8h or self.configuracion_salon.precio_particular_4h
        
        super().save(*args, **kwargs)


class CodigoSocio(models.Model):
    """Modelo para gestionar códigos válidos de socios"""
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único del socio")
    nombre_socio = models.CharField(max_length=200, help_text="Nombre del socio titular")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Código de Socio"
        verbose_name_plural = "Códigos de Socios"
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre_socio}"


class BloqueoEspacio(models.Model):
    """Modelo para bloquear espacios en fechas específicas"""
    
    MOTIVO_CHOICES = [
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('EVENTO_PRIVADO', 'Evento Privado'),
        ('REPARACION', 'Reparación'),
        ('OTRO', 'Otro'),
    ]
    
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bloqueos')
    fecha_inicio = models.DateField(help_text="Fecha de inicio del bloqueo")
    fecha_fin = models.DateField(help_text="Fecha de fin del bloqueo")
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES, default='OTRO')
    descripcion = models.TextField(blank=True, help_text="Descripción del motivo del bloqueo")
    activo = models.BooleanField(default=True, help_text="Si está activo, el bloqueo aplica")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Bloqueo de Espacio"
        verbose_name_plural = "Bloqueos de Espacios"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.salon.nombre} - {self.fecha_inicio} al {self.fecha_fin} ({self.get_motivo_display()})"
    
    def esta_bloqueado_en_fecha(self, fecha):
        """Verifica si el salón está bloqueado en una fecha específica"""
        if not self.activo:
            return False
        return self.fecha_inicio <= fecha <= self.fecha_fin


# --- Gestión de Socios (Miembros) ---
from django.contrib.auth.models import User


class Beneficio(models.Model):
    """Beneficios que pueden aplicarse a un socio (descuentos, prioridades, etc.)"""
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Beneficio'
        verbose_name_plural = 'Beneficios'
        ordering = ['-activo', 'nombre']

    def __str__(self):
        return self.nombre


class Socio(models.Model):
    """Registro de socios del Club"""
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ACTIVO', 'Activo'),
        ('SUSPENDIDO', 'Suspendido'),
        ('INACTIVO', 'Inactivo'),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='socio_profile')
    codigo = models.ForeignKey(CodigoSocio, on_delete=models.SET_NULL, null=True, blank=True, help_text='Código de socio asignado')
    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=250, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    beneficios = models.ManyToManyField(Beneficio, blank=True, related_name='socios')
    notas = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Socio'
        verbose_name_plural = 'Socios'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} ({self.codigo.codigo if self.codigo else 'sin código'})"

    def es_activo(self):
        return self.estado == 'ACTIVO'


class EmailLog(models.Model):
    """Registro de intentos de envío de notificaciones (email / whatsapp)."""
    CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
        ('WHATSAPP', 'WhatsApp'),
    ]

    reserva = models.ForeignKey(Reserva, on_delete=models.SET_NULL, null=True, blank=True, related_name='email_logs')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    to_email = models.EmailField(blank=True, null=True)
    to_phone = models.CharField(max_length=40, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    body_text = models.TextField(blank=True, null=True)
    body_html = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=False)
    error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Email / WhatsApp Log'
        verbose_name_plural = 'Email / WhatsApp Logs'
        ordering = ['-created_at']

    def __str__(self):
        target = self.to_email or self.to_phone or 'sin destino'
        return f"{self.get_channel_display()} -> {target} ({'OK' if self.success else 'FAIL'})"

