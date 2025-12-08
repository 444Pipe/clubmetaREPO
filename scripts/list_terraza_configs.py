import os, sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','clubelmeta.settings')
import django
django.setup()
from reservas.models import Salon, ConfiguracionSalon

terraza = Salon.objects.filter(nombre__icontains='terraza').first()
if not terraza:
    print('Terraza no encontrada')
    sys.exit(1)
print('Terraza id=', terraza.id, terraza.nombre)
configs = ConfiguracionSalon.objects.filter(salon=terraza)
for c in configs:
    print(f'id={c.id}, tipo={c.tipo_configuracion}, capacidad={c.capacidad}, p_part_4h={c.precio_particular_4h}, p_part_8h={c.precio_particular_8h}, p_socio_4h={c.precio_socio_4h}, p_socio_8h={c.precio_socio_8h}')
