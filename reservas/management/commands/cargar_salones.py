from django.core.management.base import BaseCommand
from reservas.models import Salon, ConfiguracionSalon


class Command(BaseCommand):
    help = 'Carga los datos iniciales de salones con sus configuraciones y precios'

    def handle(self, *args, **kwargs):
        self.stdout.write('Cargando salones y configuraciones...')
        
        # Primero eliminar todas las configuraciones y salones existentes
        ConfiguracionSalon.objects.all().delete()
        Salon.objects.all().delete()
        
        # Definir todos los salones con sus configuraciones
        salones_data = [
            {
                'nombre': 'Mi Llanura',
                'descripcion': 'Salón versátil para eventos sociales y corporativos.',
                'configuraciones': [
                    {'tipo': 'MESA_U', 'capacidad': 60, 'precio_s': 600000, 'precio_p': 1200000},
                    {'tipo': 'AUDITORIO', 'capacidad': 200, 'precio_s': 600000, 'precio_p': 1200000},
                    {'tipo': 'ESCUELA', 'capacidad': 100, 'precio_s': 1000000, 'precio_p': 1700000},
                    {'tipo': 'BANQUETE', 'capacidad': 100, 'precio_s': 1000000, 'precio_p': 1700000},
                ]
            },
            {
                'nombre': 'Terraza',
                'descripcion': 'Espacio al aire libre con vista campestre, perfecto para eventos sociales.',
                'configuraciones': [
                    {'tipo': 'IMPERIAL', 'capacidad': 20, 'precio_s': 0, 'precio_p': 300000, 'cortesia_socio': True},
                    {'tipo': 'BANQUETE', 'capacidad': 20, 'precio_s': 0, 'precio_p': 300000, 'cortesia_socio': True},
                ]
            },
            {
                'nombre': 'Salón Bar',
                'descripcion': 'Espacio cómodo ideal para reuniones informales y tertulias.',
                'configuraciones': [
                    {'tipo': 'IMPERIAL', 'capacidad': 50, 'precio_s': 0, 'precio_p': 300000, 'cortesia_socio': True},
                    {'tipo': 'MESA_U', 'capacidad': 30, 'precio_s': 0, 'precio_p': 300000, 'cortesia_socio': True},
                    {'tipo': 'ESCUELA', 'capacidad': 30, 'precio_s': 0, 'precio_p': 300000, 'cortesia_socio': True},
                    {'tipo': 'AUDITORIO', 'capacidad': 50, 'precio_s': 200000, 'precio_p': 400000},
                    {'tipo': 'BANQUETE', 'capacidad': 60, 'precio_s': 400000, 'precio_p': 600000},
                ]
            },
            {
                'nombre': 'Salón Empresarial',
                'descripcion': 'Salón profesional para reuniones corporativas y seminarios.',
                'configuraciones': [
                    {'tipo': 'EMPRESARIAL', 'capacidad': 25, 'precio_s': 200000, 'precio_p': 400000},
                    {'tipo': 'IMPERIAL', 'capacidad': 25, 'precio_s': 200000, 'precio_p': 400000},
                    {'tipo': 'MESA_U', 'capacidad': 25, 'precio_s': 200000, 'precio_p': 400000},
                ]
            },
            {
                'nombre': 'Salón Presidente',
                'descripcion': 'Salón de lujo dedicado a los Presidentes de la Junta Directiva.',
                'configuraciones': [
                    {'tipo': 'IMPERIAL', 'capacidad': 12, 'precio_s': 300000, 'precio_p': 600000},
                    {'tipo': 'MESA_U', 'capacidad': 12, 'precio_s': 300000, 'precio_p': 600000},
                    {'tipo': 'AUDITORIO', 'capacidad': 15, 'precio_s': 300000, 'precio_p': 600000},
                ]
            },
            {
                'nombre': 'Salón Kiosco',
                'descripcion': 'Pequeño salón íntimo para grupos reducidos.',
                'configuraciones': [
                    {'tipo': 'IMPERIAL', 'capacidad': 40, 'precio_s': 900000, 'precio_p': 600000},
                    {'tipo': 'MESA_U', 'capacidad': 50, 'precio_s': 300000, 'precio_p': 800000},
                    {'tipo': 'ESCUELA', 'capacidad': 40, 'precio_s': 300000, 'precio_p': 600000},
                    {'tipo': 'AUDITORIO', 'capacidad': 50, 'precio_s': 300000, 'precio_p': 600000},
                    {'tipo': 'BANQUETE', 'capacidad': 50, 'precio_s': 400000, 'precio_p': 800000},
                ]
            },
        ]
        
        # Crear salones y configuraciones
        for salon_data in salones_data:
            salon, created = Salon.objects.update_or_create(
                nombre=salon_data['nombre'],
                defaults={
                    'descripcion': salon_data['descripcion'],
                    'disponible': True,
                }
            )
            
            if created:
                self.stdout.write(f'✓ Creado salón: {salon.nombre}')
            else:
                self.stdout.write(f'↻ Actualizado salón: {salon.nombre}')
            
            for config_data in salon_data['configuraciones']:
                config, created = ConfiguracionSalon.objects.update_or_create(
                    salon=salon,
                    tipo_configuracion=config_data['tipo'],
                    defaults={
                        'capacidad': config_data['capacidad'],
                        'precio_socio_4h': config_data['precio_s'],
                        'precio_particular_4h': config_data['precio_p'],
                    }
                )
                cortesia = config_data.get('cortesia_socio', False)
                if cortesia:
                    precio_display = 'Socio: Cortesía / Particular: ${:,}'.format(config_data['precio_p'])
                else:
                    precio_display = 'Socio: ${:,} / Particular: ${:,}'.format(config_data['precio_s'], config_data['precio_p'])
                
                if created:
                    self.stdout.write(f'  ✓ {config.get_tipo_configuracion_display()} ({config.capacidad} PAX) - {precio_display}')
                else:
                    self.stdout.write(f'  ↻ {config.get_tipo_configuracion_display()} ({config.capacidad} PAX) - {precio_display}')
        
        self.stdout.write(self.style.SUCCESS(f'\n¡Completado! 6 salones cargados exitosamente.'))
