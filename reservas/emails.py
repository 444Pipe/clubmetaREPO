import os
import threading
import time
import traceback
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def send_email_async(subject, template_txt, template_html, context, recipient_list):
    """Render templates and send an email in a background thread."""
    try:
        text_body = render_to_string(template_txt, context)
    except Exception:
        text_body = ''
    try:
        html_body = render_to_string(template_html, context)
    except Exception:
        html_body = None

    def _worker():
        reserva = None
        try:
            if isinstance(context, dict):
                reserva = context.get('reserva')
        except Exception:
            reserva = None

        from_addr = os.getenv('EMAIL_FROM') or getattr(settings, 'DEFAULT_FROM_EMAIL', None)

        try:
            if isinstance(recipient_list, (list, tuple)):
                to_addrs = [r.strip() for r in recipient_list if r and str(r).strip()]
            elif recipient_list:
                to_addrs = [str(recipient_list).strip()]
            else:
                to_addrs = []

            if not to_addrs:
                raise RuntimeError('No recipient specified for email')

            if not from_addr:
                raise RuntimeError('No from address configured')

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=from_addr,
                to=to_addrs,
            )
            if html_body:
                msg.attach_alternative(html_body, "text/html")
            
            msg.send()

            try:
                from reservas.models import EmailLog
                EmailLog.objects.create(
                    reserva=reserva if hasattr(reserva, 'pk') else None,
                    channel='EMAIL',
                    to_email=(','.join(to_addrs) if to_addrs else None),
                    subject=subject,
                    body_text=text_body,
                    body_html=html_body,
                    success=True,
                    error=None,
                )
            except Exception:
                pass

        except Exception:
            err = traceback.format_exc()
            try:
                from reservas.models import EmailLog
                EmailLog.objects.create(
                    reserva=reserva if hasattr(reserva, 'pk') else None,
                    channel='EMAIL',
                    to_email=(','.join(to_addrs) if 'to_addrs' in locals() and to_addrs else None),
                    subject=subject,
                    body_text=text_body,
                    body_html=html_body,
                    success=False,
                    error=err,
                )
            except Exception:
                pass

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()


def send_raw_email_sync(subject, text_body, html_body, recipient_list, reserva=None):
    """Synchronous helper to send raw text/html. Returns True on success, False on failure."""
    from_addr = os.getenv('EMAIL_FROM') or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    to_addrs = list(recipient_list) if isinstance(recipient_list, (list, tuple)) else [recipient_list]

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_addr,
            to=to_addrs,
        )
        if html_body:
            msg.attach_alternative(html_body, "text/html")
        
        msg.send()

        try:
            from reservas.models import EmailLog
            EmailLog.objects.create(
                reserva=reserva if hasattr(reserva, 'pk') else None,
                channel='EMAIL',
                to_email=(','.join(to_addrs) if to_addrs else None),
                subject=subject,
                body_text=text_body,
                body_html=html_body,
                success=True,
                error=None,
            )
        except Exception:
            pass

        return True
    except Exception as e:
        err = traceback.format_exc()
        try:
            from reservas.models import EmailLog
            to_email_val = None
            try:
                if 'to_addrs' in locals() and to_addrs:
                    to_email_val = ','.join(to_addrs)
            except Exception:
                to_email_val = None

            EmailLog.objects.create(
                reserva=reserva if hasattr(reserva, 'pk') else None,
                channel='EMAIL',
                to_email=to_email_val,
                subject=subject,
                body_text=text_body,
                body_html=html_body,
                success=False,
                error=err,
            )
        except Exception:
            pass
        return False
