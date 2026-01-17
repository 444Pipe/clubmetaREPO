import os
import threading
import traceback
from django.template.loader import render_to_string
from django.conf import settings

try:
    from resend import Resend
except Exception:
    Resend = None


def _get_resend_client():
    api_key = os.getenv('RESEND_API_KEY')
    if not api_key or Resend is None:
        return None
    return Resend(api_key)


def send_email_async(subject, template_txt, template_html, context, recipient_list):
    """Render templates and send an email via Resend in a background thread.

    Signature kept intentionally compatible with existing callers.
    If Resend is not configured or an exception occurs, the function will
    still record an EmailLog and will not raise, preserving application flow.
    """

    # Pre-render bodies so logs always have content
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

        client = _get_resend_client()
        from_addr = os.getenv('EMAIL_FROM') or getattr(settings, 'DEFAULT_FROM_EMAIL', None)

        try:
            if client is None:
                raise RuntimeError('Resend client not configured (RESEND_API_KEY missing or library not installed)')

            # Normalize recipient list: accept string or list/tuple, strip and remove empty
            if isinstance(recipient_list, (list, tuple)):
                to_addrs = [r.strip() for r in recipient_list if r and str(r).strip()]
            elif recipient_list:
                to_addrs = [str(recipient_list).strip()]
            else:
                to_addrs = []

            if not to_addrs:
                raise RuntimeError('No recipient specified for email')

            if not from_addr:
                raise RuntimeError('No from address configured (EMAIL_FROM or DEFAULT_FROM_EMAIL)')

            # Send via Resend API
            client.emails.send(
                from_=from_addr,
                to=to_addrs,
                subject=subject,
                html=html_body or text_body,
                text=text_body or None,
            )

            # Log success
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
    """Synchronous helper to send raw text/html using Resend (used by scripts/management commands).

    Returns True on success, False on failure. Does not raise.
    """
    client = _get_resend_client()
    from_addr = os.getenv('EMAIL_FROM') or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    to_addrs = list(recipient_list) if isinstance(recipient_list, (list, tuple)) else [recipient_list]

    try:
        if client is None:
            raise RuntimeError('Resend client not configured (RESEND_API_KEY missing or library not installed)')

        client.emails.send(
            from_=from_addr,
            to=to_addrs,
            subject=subject,
            html=html_body or text_body,
            text=text_body or None,
        )

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
