import os
import sys
from pathlib import Path

# Preparar entorno Django
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubelmeta.settings')

import django
django.setup()

from reservas.models import Salon, ConfiguracionSalon

TERMINAL = print

def update():
    try:
        terraza = Salon.objects.filter(nombre__icontains='terraza').first()
        if not terraza:
            TERMINAL('No se encontró un salón llamado Terraza. Revisa nombres en la base de datos.')
            return

        TERMINAL(f'Actualizando configuraciones para salón: {terraza.nombre} (id={terraza.id})')

        # IMPERIAL
        imperial = ConfiguracionSalon.objects.filter(salon=terraza, tipo_configuracion='IMPERIAL').first()
        if imperial:
            imperial.capacidad = 20
            imperial.precio_particular_4h = 300000
            imperial.precio_particular_8h = 600000
            imperial.save()
            TERMINAL(f' - IMPERIAL (id={imperial.id}) actualizado: capacidad=20, particular 4h=300000, 8h=600000')
        else:
            TERMINAL(' - No se encontró configuración IMPERIAL. Crearé una nueva.')
            ConfiguracionSalon.objects.create(
                salon=terraza,
                tipo_configuracion='IMPERIAL',
                capacidad=20,
                precio_particular_4h=300000,
                precio_particular_8h=600000,
                precio_socio_4h=0
            )
            TERMINAL(' - IMPERIAL creada.')

        # BANQUETE
        banquete = ConfiguracionSalon.objects.filter(salon=terraza, tipo_configuracion='BANQUETE').first()
        if banquete:
            banquete.capacidad = 30
            banquete.precio_particular_4h = 300000
            banquete.precio_particular_8h = 600000
            banquete.save()
            TERMINAL(f' - BANQUETE (id={banquete.id}) actualizado: capacidad=30, particular 4h=300000, 8h=600000')
        else:
            TERMINAL(' - No se encontró configuración BANQUETE. Crearé una nueva.')
            ConfiguracionSalon.objects.create(
                salon=terraza,
                tipo_configuracion='BANQUETE',
                capacidad=30,
                precio_particular_4h=300000,
                precio_particular_8h=600000,
                precio_socio_4h=0
            )
            TERMINAL(' - BANQUETE creada.')

        TERMINAL('Actualización completada.')
    except Exception as e:
        TERMINAL('Error al actualizar:', str(e))

if __name__ == '__main__':
    update()
