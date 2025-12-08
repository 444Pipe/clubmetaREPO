import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubelmeta.settings')
import django
django.setup()

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_test_email(to_address):
    subject = 'Prueba de correo - Club El Meta'
    text = 'Este es un correo de prueba enviado desde la aplicación.\nSi recibes esto, la configuración SMTP funciona.'
    html = '<p>Este es un <strong>correo de prueba</strong> enviado desde la aplicación.</p>'
    from_email = settings.DEFAULT_FROM_EMAIL

    msg = EmailMultiAlternatives(subject, text, from_email, [to_address])
    msg.attach_alternative(html, 'text/html')
    try:
        sent = msg.send(fail_silently=False)
        print('send() returned', sent)
        try:
            from reservas.models import EmailLog
            EmailLog.objects.create(reserva=None, channel='EMAIL', to_email=to_address, subject=subject, body_text=text, body_html=None, success=bool(sent), error=None)
            print('EmailLog registrado.')
        except Exception as e:
            print('No se pudo crear EmailLog:', e)
        return True
    except Exception as e:
        print('Error al enviar correo:', e)
        try:
            from reservas.models import EmailLog
            EmailLog.objects.create(reserva=None, channel='EMAIL', to_email=to_address, subject=subject, body_text=text, body_html=None, success=False, error=str(e))
            print('EmailLog (error) registrado.')
        except Exception as e2:
            print('No se pudo crear EmailLog (error):', e2)
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = 'delgadofelipe315@gmail.com'
    print('Enviando correo de prueba a', target)
    ok = send_test_email(target)
    print('Resultado:', ok)
