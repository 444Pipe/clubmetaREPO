import os
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubelmeta.settings')

django.setup()

from reservas.models import Salon, ConfiguracionSalon, Reserva, BloqueoEspacio

needle = 'Sala Test Auto'
salons = Salon.objects.filter(nombre__icontains=needle)
print('Salones encontrados:', salons.count())
for s in salons:
    print('Salon:', s.id, repr(s.nombre))
    configs = ConfiguracionSalon.objects.filter(salon=s)
    reservas = Reserva.objects.filter(configuracion_salon__salon=s)
    bloqueos = BloqueoEspacio.objects.filter(salon=s)
    print('  configs:', configs.count())
    print('  reservas:', reservas.count())
    if reservas.exists():
        print('  Reserva IDs:', list(reservas.values_list('id', flat=True)))
    print('  bloqueos:', bloqueos.count())

if salons.exists():
    # Count before delete
    reservas_qs = Reserva.objects.filter(configuracion_salon__salon__in=salons)
    cnt_res = reservas_qs.count()
    configs_qs = ConfiguracionSalon.objects.filter(salon__in=salons)
    cnt_configs = configs_qs.count()
    bloqueos_qs = BloqueoEspacio.objects.filter(salon__in=salons)
    cnt_bloq = bloqueos_qs.count()
    cnt_sal = salons.count()

    # Perform deletions
    deleted_res = reservas_qs.delete()
    deleted_configs = configs_qs.delete()
    deleted_bloq = bloqueos_qs.delete()
    deleted_sal = salons.delete()

    print('\nResumen antes de borrar:')
    print('  Reservas a borrar:', cnt_res)
    print('  Configuraciones a borrar:', cnt_configs)
    print('  Bloqueos a borrar:', cnt_bloq)
    print('  Salones a borrar:', cnt_sal)

    print('\nResultados delete() returns (count, dict):')
    print('  reservas deleted:', deleted_res)
    print('  configs deleted:', deleted_configs)
    print('  bloqueos deleted:', deleted_bloq)
    print('  salons deleted:', deleted_sal)
else:
    print('No se encontraron salones coincidentes. Nada que borrar.')
