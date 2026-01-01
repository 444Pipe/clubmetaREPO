import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubelmeta.settings')
django.setup()

from reservas.models import Salon

OLD = 'salon mi llanura'
NEW = 'salon_mi_llanura'

q = Salon.objects.filter(imagen__icontains=OLD)
print('Found', q.count(), 'salons to update')
for s in q:
    print('Before:', s.nombre, s.imagen)
    s.imagen = s.imagen.replace(OLD, NEW)
    s.save()
    print('After:', s.nombre, s.imagen)

print('Done')
