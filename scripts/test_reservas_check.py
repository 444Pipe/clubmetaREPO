import os
import sys
import django
from decimal import Decimal
from pathlib import Path

# Ensure project root is in sys.path so 'clubelmeta' package can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubelmeta.settings')
django.setup()

from reservas.models import ConfiguracionSalon, Reserva
from datetime import date, time, timedelta


def run_test():
    config = ConfiguracionSalon.objects.first()
    if not config:
        print('No hay ConfiguracionSalon en la base de datos. Crea al menos una configuración para probar.')
        return

    evento_fecha = date.today() + timedelta(days=10)
    hora_inicio = time(10, 0)

    tests = [
        ('PARTICULAR', 'particular'),
        ('SOCIO', 'socio'),
    ]

    for tipo, label in tests:
        # crear reserva de prueba
        r = Reserva(
            configuracion_salon=config,
            nombre_cliente=f'Test {label} 8h',
            email_cliente=f'test_{label}@example.com',
            telefono_cliente='3000000000',
            tipo_cliente=tipo,
            fecha_evento=evento_fecha,
            hora_inicio=hora_inicio,
            duracion='8H',
            tiempo_decoracion=0,
            numero_personas=1,
            precio_total=0,  # dejar que el modelo calcule
            estado='PENDIENTE',
        )
        r.save()

        # Precio esperado según configuración
        if tipo == 'SOCIO':
            expected = config.precio_socio_8h or config.precio_socio_4h
        else:
            expected = config.precio_particular_8h or config.precio_particular_4h

        stored = r.precio_total

        print('---')
        print(f'Tipo: {tipo}')
        print(f'Configuracion id: {config.id} - Salon: {config.salon.nombre} - Tipo conf: {config.tipo_configuracion}')
        print(f'Expected (8h): {expected} | Stored in Reserva.precio_total: {stored}')

        # Limpieza: eliminar la reserva creada
        r.delete()


if __name__ == '__main__':
    run_test()
