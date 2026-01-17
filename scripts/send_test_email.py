import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubelmeta.settings')
import django
django.setup()

from django.conf import settings
from reservas.emails import send_raw_email_sync


def send_test_email(to_address):
    subject = 'Prueba de correo - Club El Meta'
    text = 'Este es un correo de prueba enviado desde la aplicación.\nSi recibes esto, la configuración SMTP funciona.'
    html = '<p>Este es un <strong>correo de prueba</strong> enviado desde la aplicación.</p>'
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        ok = send_raw_email_sync(subject, text, html, [to_address], reserva=None)
        print('Resultado envio:', ok)
        return ok
    except Exception as e:
        print('Error al enviar correo (unexpected):', e)
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = 'delgadofelipe315@gmail.com'
    print('Enviando correo de prueba a', target)
    ok = send_test_email(target)
    print('Resultado:', ok)
