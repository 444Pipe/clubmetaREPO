from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.

class Salon(models.Model):
    """Modelo para representar los salones del club"""
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, help_text="Descripción del salón")
    imagen = models.CharField(max_length=200, blank=True, help_text="Ruta de la imagen del salón")
    disponible = models.BooleanField(default=True)
    # Medidas del salón (metros)
    largo_m = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Largo en metros (opcional)")
    ancho_m = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Ancho en metros (opcional)")
    alto_m = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Alto en metros (opcional)")
    # Para espacios circulares o que usen diámetro
    diametro_m = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Diámetro en metros (opcional)")
    # Medidas de tarima (si aplica)
    tarima_largo_m = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Largo de la tarima en metros (opcional)")
    tarima_ancho_m = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Ancho de la tarima en metros (opcional)")
    tarima_alto_m = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Alto de la tarima en metros (opcional)")
    
    class Meta:
        verbose_name = "Salón"
        verbose_name_plural = "Salones"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

    def medidas_dict(self):
        """Devuelve un diccionario con las medidas formateadas (None si no aplican)."""
        return {
            'largo_m': self.largo_m,
            'ancho_m': self.ancho_m,
            'alto_m': self.alto_m,
            'diametro_m': self.diametro_m,
            'tarima_largo_m': self.tarima_largo_m,
            'tarima_ancho_m': self.tarima_ancho_m,
            'tarima_alto_m': self.tarima_alto_m,
        }


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
    # Ruta relativa a la imagen del montaje dentro de `static/img/` (ej: "montajes/mi_llanura/auditorio.jpg")
    imagen_montaje = models.CharField(max_length=300, blank=True, help_text="Ruta relativa en static/img/ para la imagen de este montaje")
    
    class Meta:
        verbose_name = "Configuración de Salón"
        verbose_name_plural = "Configuraciones de Salones"
        ordering = ['salon__nombre', 'tipo_configuracion']
        unique_together = ['salon', 'tipo_configuracion']
        # Permiso específico para modificación de precios/configuración (solo Administrador General)
        permissions = (
            ("can_modify_prices", "Puede modificar precios y parámetros del sistema"),
        )
    
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
        # Permisos personalizados para control fino desde grupos
        permissions = (
            ("can_review_reserva", "Puede revisar reservas"),
            ("can_confirm_reserva", "Puede confirmar reservas"),
            ("can_reject_reserva", "Puede rechazar/cancelar reservas"),
        )
    
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
        
        # Validate required fields at model level
        try:
            self.full_clean()
        except ValidationError:
            # Re-raise to make validation failures explicit to callers
            raise

        super().save(*args, **kwargs)

    def clean(self):
        """Validaciones de modelo: exigir email del cliente."""
        super().clean()
        if not self.email_cliente or not str(self.email_cliente).strip():
            raise ValidationError({'email_cliente': 'El correo del cliente es obligatorio.'})



class EmailLog(models.Model):
    """Registro de intentos de envío de correos electrónicos."""
    CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
    ]

    reserva = models.ForeignKey(Reserva, on_delete=models.SET_NULL, null=True, blank=True, related_name='email_logs')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='EMAIL')
    to_email = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    body_text = models.TextField(blank=True, null=True)
    body_html = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=False)
    error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-created_at']

    def __str__(self):
        target = self.to_email or 'sin destino'
        return f"{self.get_channel_display()} -> {target} ({'OK' if self.success else 'FAIL'})"
class CodigoSocio(models.Model):
    """Modelo para gestionar códigos válidos de socios"""
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único del socio")
    nombre_socio = models.CharField(max_length=200, help_text="Nombre del socio titular")
    email = models.EmailField(blank=True, null=True, help_text='Email del socio')
    identificacion = models.CharField(max_length=50, blank=True, null=True, help_text='Número de identificación / cédula')
    celular = models.CharField(max_length=30, blank=True, null=True, help_text='Número de celular')
    direccion = models.CharField(max_length=250, blank=True, null=True, help_text='Dirección del socio')
    empresa = models.CharField(max_length=200, blank=True, null=True, help_text='Empresa o entidad del socio (opcional)')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Código de Socio"
        verbose_name_plural = "Códigos de Socios"
        ordering = ['codigo']
    
    def __str__(self):
        id_text = f" - {self.identificacion}" if self.identificacion else ''
        return f"{self.codigo} - {self.nombre_socio}{id_text}"


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
    hora_inicio = models.TimeField(null=True, blank=True, help_text="Hora de inicio (opcional)")
    fecha_fin = models.DateField(help_text="Fecha de fin del bloqueo")
    hora_fin = models.TimeField(null=True, blank=True, help_text="Hora de fin (opcional)")
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES, default='OTRO')
    descripcion = models.TextField(blank=True, help_text="Descripción del motivo del bloqueo")
    activo = models.BooleanField(default=True, help_text="Si está activo, el bloqueo aplica")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Bloqueo de Espacio"
        verbose_name_plural = "Bloqueos de Espacios"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        times = ''
        if self.hora_inicio or self.hora_fin:
            hi = self.hora_inicio.strftime('%H:%M') if self.hora_inicio else '--:--'
            hf = self.hora_fin.strftime('%H:%M') if self.hora_fin else '--:--'
            times = f' {hi}–{hf}'
        return f"{self.salon.nombre} - {self.fecha_inicio} {times} al {self.fecha_fin} ({self.get_motivo_display()})"
    
    def esta_bloqueado_en_fecha(self, fecha):
        """Verifica si el salón está bloqueado en una fecha específica"""
        if not self.activo:
            return False
        return self.fecha_inicio <= fecha <= self.fecha_fin


class ServicioAdicional(models.Model):
    """Modelo para servicios adicionales que se pueden agregar a las reservas"""
    
    nombre = models.CharField(max_length=200, help_text="Nombre del servicio adicional")
    descripcion = models.TextField(blank=True, help_text="Descripción detallada del servicio")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio por unidad")
    unidad_medida = models.CharField(max_length=50, default="Unidad", help_text="Ej: Persona, Mesa, Hora")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Servicio Adicional"
        verbose_name_plural = "Servicios Adicionales"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio_unitario:,.0f} por {self.unidad_medida}"


class ReservaServicioAdicional(models.Model):
    """Modelo intermedio para relacionar reservas con servicios adicionales"""
    
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='servicios_adicionales')
    servicio = models.ForeignKey(ServicioAdicional, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio al momento de la reserva")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cantidad × Precio unitario")
    notas = models.TextField(blank=True, help_text="Notas específicas para este servicio")
    
    class Meta:
        verbose_name = "Servicio Adicional de Reserva"
        verbose_name_plural = "Servicios Adicionales de Reservas"
        ordering = ['servicio__nombre']
    
    def __str__(self):
        return f"{self.reserva} - {self.servicio.nombre} (x{self.cantidad})"
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente el subtotal"""
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)


class Comunicado(models.Model):
    """Comunicados de Gerencia (para la sección pública)."""
    titulo = models.CharField(max_length=255)
    cuerpo = models.TextField(blank=True)
    publicado = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Comunicado'
        verbose_name_plural = 'Comunicados'
        ordering = ['-publicado']

    def __str__(self):
        return self.titulo


class ComunicadoImagen(models.Model):
    comunicado = models.ForeignKey(Comunicado, on_delete=models.CASCADE, related_name='images')
    imagen = models.ImageField(upload_to='comunicados/%Y/%m/%d/')
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Imagen de Comunicado'
        verbose_name_plural = 'Imágenes de Comunicados'
        ordering = ['orden', 'id']

    def __str__(self):
        return f"Imagen {self.id} - {self.comunicado.titulo[:30]}"


