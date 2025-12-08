from threading import Thread
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_email_async(subject, template_txt, template_html, context, recipient_list):
    def _send():
        text_body = render_to_string(template_txt, context)
        html_body = render_to_string(template_html, context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=True)

    Thread(target=_send).start()
