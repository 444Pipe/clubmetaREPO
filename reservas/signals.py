from django.db.models.signals import post_save, pre_save
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from reservas.utils.email_async import send_email_async
import traceback


def _render_message(subject, template_txt, template_html, context):
    """Render templates and return (text_content, html_content)."""
    text_content = ''
    html_content = None
    try:
        text_content = render_to_string(template_txt, context)
    except Exception:
        text_content = ''
    try:
        html_content = render_to_string(template_html, context)
    except Exception:
        html_content = None

    if not text_content and html_content:
        try:
            text_content = strip_tags(html_content).strip()
        except Exception:
            text_content = ''

    if not text_content:
        text_content = subject

    return text_content, html_content


def _save_email_log(reserva, to_email, subject, body_text, body_html, success, error):
    """Helper to persist EmailLog entries, swallowing any errors during logging."""
    try:
        from .models import EmailLog
        EmailLog.objects.create(
            reserva=reserva if getattr(reserva, 'pk', None) else None,
            channel='EMAIL',
            to_email=to_email,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            success=bool(success),
            error=error if error else None,
        )
    except Exception:
        pass


def reserva_pre_save(sender, instance, **kwargs):
    """Guardar el estado previo antes de guardar la reserva para detectar transiciones."""
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_estado = old.estado
        except Exception:
            instance._old_estado = None


def reserva_post_save(sender, instance, created, **kwargs):
    """Enviar correos cuando se crea una reserva o cuando cambia a CONFIRMADA."""

    # 🟦 COMPORTAMIENTO AL CREAR
    if created:
        context = {
            'reserva': instance,
            'cliente': instance.nombre_cliente,
            'precio': instance.precio_total,
        }

        # 🟩 1. ENVÍO AL CLIENTE
        if instance.email_cliente:
            subject = f"Confirmación de Reserva #{instance.id} - {instance.configuracion_salon.salon.nombre}"
            txt, html = _render_message(subject,
                                        'reservas/emails/reserva_cliente.txt',
                                        'reservas/emails/reserva_cliente.html',
                                        context)
            try:
                # (🟢 FIX → argumentos POSICIONALES)
                send_email_async(
                    subject,
                    'reservas/emails/reserva_cliente.txt',
                    'reservas/emails/reserva_cliente.html',
                    context,
                    [instance.email_cliente]
                )
                success, error = True, None
            except Exception:
                success, error = False, traceback.format_exc()

            _save_email_log(instance, instance.email_cliente, subject, txt, html, success, error)

        # 🟨 2. SI ES SOCIO → NOTIFICAR
        if instance.tipo_cliente == 'SOCIO':
            try:
                from .models import Socio
                socio = Socio.objects.filter(email__iexact=instance.email_cliente).first()
                if socio and socio.email:
                    subject = f"Notificación de Reserva Socio #{instance.id} - {socio.nombre}"
                    txt, html = _render_message(subject,
                                                'reservas/emails/reserva_socio.txt',
                                                'reservas/emails/reserva_socio.html',
                                                {**context, 'socio': socio})
                    try:
                        send_email_async(
                            subject,
                            'reservas/emails/reserva_socio.txt',
                            'reservas/emails/reserva_socio.html',
                            {**context, 'socio': socio},
                            [socio.email]
                        )
                        success, error = True, None
                    except Exception:
                        success, error = False, traceback.format_exc()

                    _save_email_log(instance, socio.email, subject, txt, html, success, error)
            except Exception:
                pass

        # 🟥 3. COPIA AL ADMIN
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        if admin_email:
            try:
                subject = f"Nueva Reserva #{instance.id} - {instance.configuracion_salon.salon.nombre}"
                txt, html = _render_message(subject,
                                            'reservas/emails/reserva_admin.txt',
                                            'reservas/emails/reserva_admin.html',
                                            {**context, 'admin': True})
                try:
                    send_email_async(
                        subject,
                        'reservas/emails/reserva_admin.txt',
                        'reservas/emails/reserva_admin.html',
                        {**context, 'admin': True},
                        [admin_email]
                    )
                    success, error = True, None
                except Exception:
                    success, error = False, traceback.format_exc()

                _save_email_log(instance, admin_email, subject, txt, html, success, error)
            except Exception:
                pass

        return

    # 🟦 COMPORTAMIENTO AL CONFIRMAR RESERVA
    old_estado = getattr(instance, '_old_estado', None)
    if old_estado != instance.estado and instance.estado == 'CONFIRMADA':

        subject = f"Reserva Confirmada #{instance.id} - {instance.configuracion_salon.salon.nombre}"
        context = {
            'reserva': instance,
            'cliente': instance.nombre_cliente,
            'precio': instance.precio_total,
        }

        try:
            txt, html = _render_message(subject,
                                        'reservas/emails/reserva_confirmada.txt',
                                        'reservas/emails/reserva_confirmada.html',
                                        context)
            try:
                send_email_async(
                    subject,
                    'reservas/emails/reserva_confirmada.txt',
                    'reservas/emails/reserva_confirmada.html',
                    context,
                    [instance.email_cliente]
                )
                success, error = True, None
            except Exception:
                success, error = False, traceback.format_exc()
        except Exception:
            txt, html = '', None
            success = False
            error = traceback.format_exc()

        # Log
        _save_email_log(instance, instance.email_cliente, subject, txt, html, success, error)


# La conexión a post_save se realiza en apps.ReservasConfig.ready()
