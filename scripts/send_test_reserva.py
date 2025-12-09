import os
import django
import time
import traceback
import sys

# Ensure project root is on sys.path so `clubelmeta` package is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubelmeta.settings')
django.setup()

from reservas.models import Salon, ConfiguracionSalon, Reserva, EmailLog

def create_test_reserva():
    salon, _ = Salon.objects.get_or_create(nombre='Sala Test Auto')
    conf, created = ConfiguracionSalon.objects.get_or_create(
        salon=salon,
        tipo_configuracion='BANQUETE',
        defaults={
            'capacidad': 10,
            'precio_socio_4h': 100,
            'precio_particular_4h': 200,
            'precio_socio_8h': 200,
            'precio_particular_8h': 400,
        }
    )

    r = Reserva.objects.create(
        configuracion_salon=conf,
        nombre_cliente='Test Envío',
        email_cliente='delgadofelipe315@gmail.com',
        telefono_cliente='3000000000',
        tipo_cliente='PARTICULAR',
        fecha_evento='2025-12-31',
        numero_personas=2,
        precio_total=100,
    )
    return r


if __name__ == '__main__':
    try:
        print('Creating test reserva...')
        r = create_test_reserva()
        print('Reserva created id=', r.pk)
        print('Waiting 6 seconds for background send...')
        time.sleep(6)

        last = EmailLog.objects.order_by('-created_at').first()
        if not last:
            print('No EmailLog entries found.')
        else:
            print('Latest EmailLog id=', last.pk)
            print('to_email=', last.to_email)
            print('success=', last.success)
            print('error=', last.error)
            print('body_text (first 200 chars)=')
            print((last.body_text or '')[:200])

        logs_for_reserva = EmailLog.objects.filter(reserva=r).order_by('-created_at')
        print('EmailLog count for this reserva:', logs_for_reserva.count())
        for e in logs_for_reserva:
            print(' ->', e.pk, e.to_email, e.success, (e.error or '')[:120])

    except Exception:
        print('Exception during test:')
        traceback.print_exc()
