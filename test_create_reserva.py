import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubelmeta.settings')
import django
django.setup()
from reservas.models import Reserva, ConfiguracionSalon
from datetime import date, time

config = ConfiguracionSalon.objects.get(id=22)
print('Using config', config.id)

r = Reserva.objects.create(
    configuracion_salon=config,
    nombre_cliente='Test User',
    email_cliente='test@example.com',
    telefono_cliente='3000000000',
    tipo_cliente='SOCIO',
    fecha_evento=date.today(),
    hora_inicio=time(12,0),
    duracion='8H',
    tiempo_decoracion=0,
    numero_personas=10,
    precio_total=0,
    estado='PENDIENTE',
    observaciones='Prueba'
)

print('Created Reserva id', r.id)
print('Stored precio_total before refresh:', r.precio_total)
r.refresh_from_db()
print('After refresh precio_total:', r.precio_total)
print('Config 4h/8h socio:', config.precio_socio_4h, config.precio_socio_8h)
