from decimal import Decimal
from django.core.management.base import BaseCommand

from reservas.models import Salon, ConfiguracionSalon
from reservas.views import get_salon_images


SALONES_DATA = {
    'Mi Llanura': {
        'configs': {
            'MESA_U': {
                'capacidad': 60,
                'socio_4h': Decimal('600000'),
                'socio_8h': Decimal('1200000'),
                'part_4h': Decimal('1500000'),
                'part_8h': Decimal('2500000'),
            },
            'AUDITORIO': {
                'capacidad': 100,
                'socio_4h': Decimal('600000'),
                'socio_8h': Decimal('1200000'),
                'part_4h': Decimal('1500000'),
                'part_8h': Decimal('2500000'),
            },
            'ESCUELA': {
                'capacidad': 100,
                'socio_4h': Decimal('1000000'),
                'socio_8h': Decimal('1700000'),
                'part_4h': Decimal('1900000'),
                'part_8h': Decimal('2800000'),
            },
            'BANQUETE': {
                'capacidad': 100,
                'socio_4h': Decimal('1000000'),
                'socio_8h': Decimal('1700000'),
                'part_4h': Decimal('1900000'),
                'part_8h': Decimal('2800000'),
            }
        }
    },
    'Salón Bar': {
        'configs': {
            'IMPERIAL': {
                'capacidad': 30,
                'socio_4h': Decimal('0'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('400000'),
                'part_8h': Decimal('800000'),
            },
            'MESA_U': {
                'capacidad': 30,
                'socio_4h': Decimal('0'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('400000'),
                'part_8h': Decimal('800000'),
            },
            'ESCUELA': {
                'capacidad': 30,
                'socio_4h': Decimal('0'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('400000'),
                'part_8h': Decimal('800000'),
            },
            'AUDITORIO': {
                'capacidad': 50,
                'socio_4h': Decimal('200000'),
                'socio_8h': Decimal('400000'),
                'part_4h': Decimal('400000'),
                'part_8h': Decimal('800000'),
            },
            'BANQUETE': {
                'capacidad': 60,
                'socio_4h': Decimal('400000'),
                'socio_8h': Decimal('600000'),
                'part_4h': Decimal('700000'),
                'part_8h': Decimal('1000000'),
            }
        }
    },
    'Salón Empresarial': {
        'configs': {
            'IMPERIAL': {
                'capacidad': 25,
                'socio_4h': Decimal('200000'),
                'socio_8h': Decimal('400000'),
                'part_4h': Decimal('400000'),
                'part_8h': Decimal('600000'),
            },
            'MESA_U': {
                'capacidad': 25,
                'socio_4h': Decimal('200000'),
                'socio_8h': Decimal('400000'),
                'part_4h': Decimal('400000'),
                'part_8h': Decimal('800000'),
            },
            'AUDITORIO': {
                'capacidad': 35,
                'socio_4h': Decimal('200000'),
                'socio_8h': Decimal('400000'),
                'part_4h': Decimal('400000'),
                'part_8h': Decimal('800000'),
            }
        }
    },
    'Terraza': {
        'configs': {
            'IMPERIAL': {
                'capacidad': 20,
                'socio_4h': Decimal('0'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('300000'),
                'part_8h': Decimal('600000'),
            },
            'BANQUETE': {
                'capacidad': 30,
                'socio_4h': Decimal('0'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('300000'),
                'part_8h': Decimal('600000'),
            }
        }
    },
    'Salón Kiosco': {
        'configs': {
            'IMPERIAL': {
                'capacidad': 30,
                'socio_4h': Decimal('0'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('300000'),
                'part_8h': Decimal('600000'),
            },
            'MESA_U': {
                'capacidad': 30,
                'socio_4h': Decimal('0'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('300000'),
                'part_8h': Decimal('600000'),
            },
            'ESCUELA': {
                'capacidad': 30,
                'socio_4h': Decimal('0'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('300000'),
                'part_8h': Decimal('600000'),
            },
            'AUDITORIO': {
                'capacidad': 50,
                'socio_4h': Decimal('200000'),
                'socio_8h': Decimal('400000'),
                'part_4h': Decimal('300000'),
                'part_8h': Decimal('600000'),
            },
            'BANQUETE': {
                'capacidad': 60,
                'socio_4h': Decimal('200000'),
                'socio_8h': Decimal('400000'),
                'part_4h': Decimal('400000'),
                'part_8h': Decimal('800000'),
            }
        }
    },
    'Salón Presidente': {
        'configs': {
            'EMPRESARIAL': {
                'capacidad': 12,
                'socio_4h': Decimal('150000'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('300000'),
                'part_8h': Decimal('600000'),
            },
            'MESA_U': {
                'capacidad': 12,
                'socio_4h': Decimal('150000'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('300000'),
                'part_8h': Decimal('600000'),
            },
            'AUDITORIO': {
                'capacidad': 15,
                'socio_4h': Decimal('150000'),
                'socio_8h': Decimal('300000'),
                'part_4h': Decimal('300000'),
                'part_8h': Decimal('600000'),
            }
        }
    }
}


class Command(BaseCommand):
    help = 'Importa/actualiza los salones y sus configuraciones desde datos predefinidos. No sobreescribe datos existentes.'

    def handle(self, *args, **options):
        created_salones = 0
        created_configs = 0
        skipped_configs = 0

        for salon_nombre, data in SALONES_DATA.items():
            # Buscar salon existente por nombre (case-insensitive)
            salon = Salon.objects.filter(nombre__iexact=salon_nombre).first()
            if salon:
                self.stdout.write(self.style.NOTICE(f"Salon existente: {salon_nombre} (id={salon.id})"))
            else:
                salon = Salon.objects.create(nombre=salon_nombre, descripcion='')
                created_salones += 1
                self.stdout.write(self.style.SUCCESS(f"Salon creado: {salon_nombre} (id={salon.id})"))

            # Asociar imagen si no existe
            try:
                images = get_salon_images(salon.nombre)
            except Exception:
                images = []

            if not salon.imagen and images:
                salon.imagen = images[0]
                salon.save()
                self.stdout.write(self.style.SUCCESS(f'Imagen asignada a {salon.nombre}: {salon.imagen}'))

            # Configuraciones
            for tipo, conf in data.get('configs', {}).items():
                config = ConfiguracionSalon.objects.filter(salon=salon, tipo_configuracion=tipo).first()
                if config:
                    # No sobrescribir datos existentes; solo completar campos vacíos si aplica
                    updated = False
                    if (not config.capacidad or config.capacidad == 0) and conf.get('capacidad'):
                        config.capacidad = conf.get('capacidad')
                        updated = True

                    # Precios: solo asignar si están vacíos o null
                    if (config.precio_socio_4h is None or config.precio_socio_4h == 0) and conf.get('socio_4h') is not None:
                        config.precio_socio_4h = conf.get('socio_4h')
                        updated = True
                    if (config.precio_socio_8h is None or config.precio_socio_8h == 0) and conf.get('socio_8h') is not None:
                        config.precio_socio_8h = conf.get('socio_8h')
                        updated = True
                    if (config.precio_particular_4h is None or config.precio_particular_4h == 0) and conf.get('part_4h') is not None:
                        config.precio_particular_4h = conf.get('part_4h')
                        updated = True
                    if (config.precio_particular_8h is None or config.precio_particular_8h == 0) and conf.get('part_8h') is not None:
                        config.precio_particular_8h = conf.get('part_8h')
                        updated = True

                    if updated:
                        config.save()
                        created_configs += 1
                        self.stdout.write(self.style.SUCCESS(f'Configuración actualizada para {salon.nombre} - {tipo}'))
                    else:
                        skipped_configs += 1
                        self.stdout.write(self.style.NOTICE(f'Se omitió configuración existente {salon.nombre} - {tipo}'))
                else:
                    # Crear nueva configuración
                    ConfiguracionSalon.objects.create(
                        salon=salon,
                        tipo_configuracion=tipo,
                        capacidad=conf.get('capacidad') or 0,
                        precio_socio_4h=conf.get('socio_4h') or Decimal('0'),
                        precio_socio_8h=conf.get('socio_8h'),
                        precio_particular_4h=conf.get('part_4h') or Decimal('0'),
                        precio_particular_8h=conf.get('part_8h'),
                    )
                    created_configs += 1
                    self.stdout.write(self.style.SUCCESS(f'Configuración creada: {salon.nombre} - {tipo}'))

        self.stdout.write(self.style.SUCCESS(f"Salones creados: {created_salones}"))
        self.stdout.write(self.style.SUCCESS(f"Configuraciones creadas/actualizadas: {created_configs}"))
        self.stdout.write(self.style.NOTICE(f"Configuraciones omitidas (existentes): {skipped_configs}"))
