from django.apps import AppConfig


class ReservasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservas'
    def ready(self):
        # Import signals and explicitly connect the reserva_post_save handler
        # to avoid import-time circular references and ensure the handler
        # is registered when the app is ready.
        try:
            from django.db.models.signals import post_save, pre_save
            from . import signals as signals_module
            # Import Reserva lazily to avoid circular imports during app import
            from .models import Reserva
            post_save.connect(signals_module.reserva_post_save, sender=Reserva)
            pre_save.connect(signals_module.reserva_pre_save, sender=Reserva)
        except Exception as e:
            import logging
            logging.exception("Error registrando señales en reservas.apps.ready(): %s", e)
            # Do not re-raise to avoid breaking startup in production,
            # but the exception is now logged for diagnosis.
