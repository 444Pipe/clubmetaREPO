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


def reserva_pre_save(sender, instance, **kwargs):
    """Guardar el estado previo antes de guardar la reserva para detectar transiciones."""
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_estado = old.estado
        except Exception:
            instance._old_estado = None


def reserva_post_save(sender, instance, created, **kwargs):
    """Enviar correos cuando se crea una reserva o cuando cambia a CONFIRMADA.

    - Al crear: envía correo de notificación al cliente/socio/admin (comportamiento original).
    - Si en una actualización la reserva cambia su `estado` a `CONFIRMADA`, envía un
      correo real al `email_cliente` con los datos mínimos.
    """
    # Comportamiento al crear (igual que antes)
    if created:
        context = {
            'reserva': instance,
            'cliente': instance.nombre_cliente,
            'precio': instance.precio_total,
        }

        # Enviar al cliente
        if instance.email_cliente:
            subject = f"Confirmación de Reserva #{instance.id} - {instance.configuracion_salon.salon.nombre}"
            txt, html = _render_message(subject,
                                        'reservas/emails/reserva_cliente.txt',
                                        'reservas/emails/reserva_cliente.html',
                                        context)
            try:
                # enviar en background (no bloquear request)
                send_email_async(
                    subject=subject,
                    template_txt='reservas/emails/reserva_cliente.txt',
                    template_html='reservas/emails/reserva_cliente.html',
                    context=context,
                    recipient_list=[instance.email_cliente]
                )
                success, error = True, None
            except Exception:
                success, error = False, traceback.format_exc()

            try:
                from .models import EmailLog
                EmailLog.objects.create(
                    reserva=instance,
                    channel='EMAIL',
                    to_email=instance.email_cliente,
                    subject=subject,
                    body_text=txt,
                    body_html=html,
                    success=bool(success),
                    error=error if error else None,
                )
            except Exception as e:
                import logging
                logging.exception("Fallo al crear EmailLog (cliente, creación reserva): %s", e)

        # Si es socio, intentar notificar al registro de socio asociado
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
                            subject=subject,
                            template_txt='reservas/emails/reserva_socio.txt',
                            template_html='reservas/emails/reserva_socio.html',
                            context={**context, 'socio': socio},
                            recipient_list=[socio.email]
                        )
                        success, error = True, None
                    except Exception:
                        success, error = False, traceback.format_exc()
                    try:
                        from .models import EmailLog
                        EmailLog.objects.create(
                            reserva=instance,
                            channel='EMAIL',
                            to_email=socio.email,
                            subject=subject,
                            body_text=txt,
                            body_html=html,
                            success=bool(success),
                            error=error if error else None,
                        )
                    except Exception as e:
                        import logging
                        logging.exception("Fallo al crear EmailLog (socio): %s", e)
            except Exception:
                pass

        # Enviar copia al admin si está configurado
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
                        subject=subject,
                        template_txt='reservas/emails/reserva_admin.txt',
                        template_html='reservas/emails/reserva_admin.html',
                        context={**context, 'admin': True},
                        recipient_list=[admin_email]
                    )
                    success, error = True, None
                except Exception:
                    success, error = False, traceback.format_exc()
                try:
                    from .models import EmailLog
                    EmailLog.objects.create(
                        reserva=instance,
                        channel='EMAIL',
                        to_email=admin_email,
                        subject=subject,
                        body_text=txt,
                        body_html=html,
                        success=bool(success),
                        error=error if error else None,
                    )
                except Exception as e:
                    import logging
                    logging.exception("Fallo al crear EmailLog (admin): %s", e)
            except Exception:
                pass
        return

    # En actualización: detectar transición de estado a CONFIRMADA
    old_estado = getattr(instance, '_old_estado', None)
    if old_estado != instance.estado and instance.estado == 'CONFIRMADA':
        # Usar plantillas para correo de confirmación (HTML + TXT)
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
                    subject=subject,
                    template_txt='reservas/emails/reserva_confirmada.txt',
                    template_html='reservas/emails/reserva_confirmada.html',
                    context=context,
                    recipient_list=[instance.email_cliente]
                )
                success, error = True, None
            except Exception:
                success, error = False, traceback.format_exc()
        except Exception:
            success = False
            error = traceback.format_exc()
            txt = ''
            html = None

        # Registrar intento en EmailLog (guardar también body_html si está disponible)
        try:
            from .models import EmailLog
            EmailLog.objects.create(
                reserva=instance,
                channel='EMAIL',
                to_email=instance.email_cliente,
                subject=subject,
                body_text=txt,
                body_html=html,
                success=bool(success),
                error=error if error else None,
            )
        except Exception as e:
            import logging
            logging.exception("Fallo al crear EmailLog (confirmación): %s", e)


# La conexión a `post_save` se realiza en `reservas.apps.ReservasConfig.ready()`
# para evitar registros globales que disparen el handler para otros modelos.
