import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubelmeta.settings')
sys.path.append(r'C:\Users\juane\Downloads\club-meta')
import django

django.setup()

from reservas.models import Salon

qs = Salon.objects.filter(nombre__istartswith='AutoTest')
count = qs.count()
print('Encontrados', count, 'salones que empiezan con "AutoTest".')
if count:
    names = list(qs.values_list('nombre', flat=True))
    qs.delete()
    print('Borrados:', names)
else:
    print('Nada para borrar.')
