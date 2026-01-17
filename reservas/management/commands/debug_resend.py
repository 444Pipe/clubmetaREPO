from django.core.management.base import BaseCommand
import os
import importlib
from django.conf import settings


class Command(BaseCommand):
    help = 'Debug Resend email config: show env, lib, try sending, and list recent EmailLog entries.'

    def add_arguments(self, parser):
        parser.add_argument('--to', help='Email address to send a test message to', required=False)
        parser.add_argument('--show-logs', action='store_true', help='Show last 20 EmailLog entries')

    def handle(self, *args, **options):
        to_addr = options.get('to')
        show_logs = options.get('show_logs')

        # Env vars
        self.stdout.write('Environment variables:')
        api_key = os.getenv('RESEND_API_KEY')
        from_addr = os.getenv('EMAIL_FROM') or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        admin = os.getenv('EMAIL_ADMIN')
        self.stdout.write(f'  RESEND_API_KEY set: {bool(api_key)}')
        if api_key:
            self.stdout.write('    (API key present — not displayed)')
        self.stdout.write(f'  EMAIL_FROM: {from_addr}')
        self.stdout.write(f'  EMAIL_ADMIN: {admin}')

        # Resend library availability
        try:
            spec = importlib.util.find_spec('resend')
            if spec is None:
                self.stdout.write('resend library: NOT INSTALLED')
                resend = None
            else:
                import resend
                v = getattr(resend, '__version__', 'unknown')
                self.stdout.write(f'resend library: INSTALLED (version={v})')
                resend = resend
        except Exception as e:
            self.stdout.write('resend library: import error: %s' % str(e))
            resend = None

        # If requested, attempt to send a test email
        if to_addr:
            self.stdout.write(f'Attempting test send to: {to_addr}')
            try:
                from reservas.emails import send_raw_email_sync
                subject = 'Prueba Resend desde debug_resend'
                text = 'Este es un correo de prueba enviado desde debug_resend management command.'
                html = '<p>Correo de prueba enviado desde <strong>debug_resend</strong>.</p>'
                ok = send_raw_email_sync(subject, text, html, [to_addr], reserva=None)
                self.stdout.write('  send_raw_email_sync returned: %s' % str(ok))
            except Exception as e:
                self.stdout.write('  Exception while sending: %s' % str(e))

        # Show recent EmailLog entries if requested
        if show_logs:
            try:
                from reservas.models import EmailLog
                qs = EmailLog.objects.order_by('-created_at')[:20]
                self.stdout.write('\nLast EmailLog entries:')
                for e in qs:
                    self.stdout.write('  - to=%s success=%s created=%s' % (e.to_email or 'sin destino', e.success, e.created_at.isoformat()))
                    if e.error:
                        # show a shortened error
                        err = e.error
                        if len(err) > 1000:
                            err = err[:1000] + '...'
                        self.stdout.write('     error: %s' % err)
            except Exception as e:
                self.stdout.write('  Could not read EmailLog: %s' % str(e))

        self.stdout.write('\nDebug complete.')
