from django.core.management.base import BaseCommand
from django.conf import settings
from reservas.emails import send_raw_email_sync

class Command(BaseCommand):
    help = 'Enviar un correo de prueba usando la configuración SMTP actual.'

    def handle(self, *args, **options):
        subject = 'Prueba SMTP'
        message = 'Esto es una prueba del sistema de correo.'
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        recipient = ['delgadofelipe315@gmail.com']
        try:
            ok = send_raw_email_sync(subject, message, None, recipient, reserva=None)
            if ok:
                self.stdout.write(self.style.SUCCESS('Correo de prueba enviado correctamente a %s' % ','.join(recipient)))
            else:
                self.stdout.write(self.style.ERROR('Error al enviar correo de prueba (ver EmailLog).'))
        except Exception as e:
            self.stdout.write(self.style.ERROR('Error al enviar correo de prueba (unexpected): %s' % str(e)))
