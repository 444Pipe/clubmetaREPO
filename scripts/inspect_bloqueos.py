from pathlib import Path
import os, sys
BASE=Path(r'C:\Users\juane\OneDrive\Desktop\clubmetaREPO')
sys.path.insert(0,str(BASE))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','clubelmeta.settings')
import django
django.setup()
from reservas.models import BloqueoEspacio
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--salon',type=int,default=1)
args=parser.parse_args()
qs=BloqueoEspacio.objects.filter(salon_id=args.salon).order_by('fecha_inicio')
print('Total:', qs.count())
for b in qs:
    print(b.id, b.salon_id, b.fecha_inicio, b.fecha_fin, b.activo, b.get_motivo_display(), b.descripcion)
