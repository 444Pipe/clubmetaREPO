import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import traceback


def send_email_async(subject, template_txt, template_html, context, recipient_list):
    """Render templates, send email in a background thread, and log result to EmailLog.

    The function signature is unchanged so callers don't need modification.
    The thread will attempt to send the message (without fail_silently) and will
    create an EmailLog record with success=True or success=False and the
    rendered bodies and error traceback when applicable.
    """

    # Pre-render bodies here so they are available for logging regardless of send result
    try:
        text_body = render_to_string(template_txt, context)
    except Exception:
        text_body = ''
    try:
        html_body = render_to_string(template_html, context)
    except Exception:
        html_body = None

    def send_email_thread():
        reserva = None
        try:
            if isinstance(context, dict):
                reserva = context.get('reserva')
        except Exception:
            reserva = None

        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                to=recipient_list
            )
            if html_body:
                msg.attach_alternative(html_body, "text/html")

            # Send without silencing exceptions so we can capture failures
            msg.send()

            # Log success
            try:
                from reservas.models import EmailLog
                EmailLog.objects.create(
                    reserva=reserva if hasattr(reserva, 'pk') else None,
                    channel='EMAIL',
                    to_email=(','.join(recipient_list) if recipient_list else None),
                    subject=subject,
                    body_text=text_body,
                    body_html=html_body,
                    success=True,
                    error=None,
                )
            except Exception:
                # don't let logging failures bubble up
                pass

        except Exception:
            err = traceback.format_exc()
            try:
                from reservas.models import EmailLog
                EmailLog.objects.create(
                    reserva=reserva if hasattr(reserva, 'pk') else None,
                    channel='EMAIL',
                    to_email=(','.join(recipient_list) if recipient_list else None),
                    subject=subject,
                    body_text=text_body,
                    body_html=html_body,
                    success=False,
                    error=err,
                )
            except Exception:
                pass

    thread = threading.Thread(target=send_email_thread, daemon=True)
    thread.start()
