from django.apps import AppConfig

class ReservasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservas'

    def ready(self):
        try:
            from django.db.models.signals import post_save, pre_save
            from .models import Reserva
            from . import signals as signals_module

            # Registrar señales correctamente
            post_save.connect(signals_module.reserva_post_save, sender=Reserva)
            pre_save.connect(signals_module.reserva_pre_save, sender=Reserva)

        except Exception as e:
            import logging
            logging.exception("Error cargando señales:", e)
