from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Enviar un correo de prueba usando la configuración SMTP actual.'

    def handle(self, *args, **options):
        subject = 'Prueba SMTP'
        message = 'Esto es una prueba del sistema de correo.'
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        recipient = ['delgadofelipe315@gmail.com']
        try:
            send_mail(subject, message, from_email, recipient, fail_silently=False)
            self.stdout.write(self.style.SUCCESS('Correo de prueba enviado correctamente a %s' % ','.join(recipient)))
        except Exception as e:
            self.stdout.write(self.style.ERROR('Error al enviar correo de prueba: %s' % str(e)))
