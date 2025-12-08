from django.db.models.signals import post_save, pre_save
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
import traceback


def send_email(subject, to_emails, template_txt, template_html, context, from_email=None):
    """Renderiza plantillas y envía un email; devuelve (success, error, text, html)."""
    from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@clubelmeta.local')
    text_content = ''
    html_content = None
    # Normalizar/sanitizar lista de destinatarios (evitar None/strings vacíos)
    try:
        to_emails = [e for e in (to_emails or []) if e]
    except Exception:
        to_emails = []
    try:
        text_content = render_to_string(template_txt, context)
    except Exception:
        text_content = ''
    try:
        html_content = render_to_string(template_html, context)
    except Exception:
        html_content = None

    # Fallback para asegurar una versión text/plain:
    # Si text_content está vacío y existe html_content, generar text desde html
    if not text_content and html_content:
        try:
            text_content = strip_tags(html_content).strip()
        except Exception:
            text_content = ''
    # Si sigue vacío, usar el subject como último recurso
    if not text_content:
        text_content = subject

    try:
        # Si no hay destinatarios válidos, no intentar enviar y devolver error claro
        if not to_emails:
            return False, 'No hay destinatarios válidos', text_content, html_content

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_emails)
        if html_content:
            msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True, None, text_content, html_content
    except Exception:
        return False, traceback.format_exc(), text_content, html_content


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
            success, error, txt, html = send_email(subject,
                                                   [instance.email_cliente],
                                                   'reservas/emails/reserva_cliente.txt',
                                                   'reservas/emails/reserva_cliente.html',
                                                   context)
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
                    success, error, txt, html = send_email(subject,
                                                           [socio.email],
                                                           'reservas/emails/reserva_socio.txt',
                                                           'reservas/emails/reserva_socio.html',
                                                           {**context, 'socio': socio})
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
                success, error, txt, html = send_email(subject,
                                                       [admin_email],
                                                       'reservas/emails/reserva_admin.txt',
                                                       'reservas/emails/reserva_admin.html',
                                                       {**context, 'admin': True})
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
            success, error, txt, html = send_email(subject,
                                                   [instance.email_cliente],
                                                   'reservas/emails/reserva_confirmada.txt',
                                                   'reservas/emails/reserva_confirmada.html',
                                                   context)
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
