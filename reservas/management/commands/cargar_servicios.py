from django.core.management.base import BaseCommand
from reservas.models import ServicioAdicional

class Command(BaseCommand):
    help = 'Carga los servicios adicionales iniciales en la base de datos'

    def handle(self, *args, **options):
        servicios = [
            # Meseros (cantidad seleccionable)
            {
                'nombre': 'Meseros',
                'descripcion': 'Cada mesero seleccionado tiene un costo fijo por evento. Selecciona cuántos meseros necesitas.',
                'precio_unitario': 120000,
                'unidad_medida': 'Mesero',
                'activo': True
            },

            # Menús de almuerzo (precio por persona)
            {
                'nombre': 'Menú Especial (2 carnes)',
                'descripcion': 'Menú especial con 2 carnes por persona',
                'precio_unitario': 70000,
                'unidad_medida': 'Persona',
                'activo': True
            },
            {
                'nombre': 'Menú Especial (1 carne)',
                'descripcion': 'Menú especial con 1 carne por persona',
                'precio_unitario': 60000,
                'unidad_medida': 'Persona',
                'activo': True
            },
            {
                'nombre': 'Menú Ejecutivo',
                'descripcion': 'Menú ejecutivo por persona',
                'precio_unitario': 40000,
                'unidad_medida': 'Persona',
                'activo': True
            },

            # Desayunos
            {
                'nombre': 'Desayuno Americano',
                'descripcion': 'Desayuno americano por persona',
                'precio_unitario': 15000,
                'unidad_medida': 'Persona',
                'activo': True
            },
            {
                'nombre': 'Desayuno Club Meta',
                'descripcion': 'Desayuno Club Meta por persona',
                'precio_unitario': 20000,
                'unidad_medida': 'Persona',
                'activo': True
            },
            {
                'nombre': 'Desayuno Tradicional',
                'descripcion': 'Desayuno tradicional por persona',
                'precio_unitario': 25000,
                'unidad_medida': 'Persona',
                'activo': True
            },
            {
                'nombre': 'Desayuno Campesino',
                'descripcion': 'Desayuno campesino por persona',
                'precio_unitario': 25000,
                'unidad_medida': 'Persona',
                'activo': True
            },

            # Refrigerios (opciones por persona)
            {
                'nombre': 'Refrigerio (12.000)',
                'descripcion': 'Refrigerio por persona - opción económica',
                'precio_unitario': 12000,
                'unidad_medida': 'Persona',
                'activo': True
            },
            {
                'nombre': 'Refrigerio (14.000)',
                'descripcion': 'Refrigerio por persona - opción intermedia',
                'precio_unitario': 14000,
                'unidad_medida': 'Persona',
                'activo': True
            },
            {
                'nombre': 'Refrigerio (20.000)',
                'descripcion': 'Refrigerio por persona - opción premium',
                'precio_unitario': 20000,
                'unidad_medida': 'Persona',
                'activo': True
            },

            # Estación de tinto (precio por persona, por defecto igual al número de personas)
            {
                'nombre': 'Estación de Tinto',
                'descripcion': 'Tinto por persona. Precio base por persona; si la reunión requiere reposición por su duración, ajusta la cantidad.',
                'precio_unitario': 3000,
                'unidad_medida': 'Persona',
                'activo': True
            }
        ]

        self.stdout.write('Cargando servicios adicionales...')
        
        for servicio_data in servicios:
            servicio, created = ServicioAdicional.objects.get_or_create(
                nombre=servicio_data['nombre'],
                defaults={
                    'descripcion': servicio_data['descripcion'],
                    'precio_unitario': servicio_data['precio_unitario'],
                    'unidad_medida': servicio_data['unidad_medida'],
                    'activo': servicio_data['activo']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Servicio creado: {servicio.nombre} - ${servicio.precio_unitario:,.0f}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'○ Servicio ya existe: {servicio.nombre}')
                )

        self.stdout.write(self.style.SUCCESS('\n¡Servicios adicionales cargados exitosamente!'))
