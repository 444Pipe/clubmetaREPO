# Script para cargar servicios adicionales usando get_or_create
# Ejecútalo con: python manage.py shell < scripts/load_servicios.py
from decimal import Decimal

from reservas.models import ServicioAdicional

SERVICIOS = [
    # Meseros
    {
        'nombre': 'Meseros',
        'descripcion': 'Servicio de meseros (por persona). Cada mesero adicional',
        'precio_unitario': Decimal('120000.00'),
        'unidad_medida': 'Mesero',
        'activo': True,
    },
    # Menús
    {
        'nombre': 'Menú Especial (2 carnes)',
        'descripcion': 'Menú especial con dos carnes. Precio por persona.',
        'precio_unitario': Decimal('70000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
    {
        'nombre': 'Menú Especial (1 carne)',
        'descripcion': 'Menú especial con una carne. Precio por persona.',
        'precio_unitario': Decimal('60000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
    {
        'nombre': 'Menú Ejecutivo',
        'descripcion': 'Menú ejecutivo. Precio por persona.',
        'precio_unitario': Decimal('40000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
    # Desayunos
    {
        'nombre': 'Desayuno Americano',
        'descripcion': 'Desayuno americano por persona.',
        'precio_unitario': Decimal('15000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
    {
        'nombre': 'Desayuno Club Meta',
        'descripcion': 'Desayuno Club Meta por persona.',
        'precio_unitario': Decimal('20000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
    {
        'nombre': 'Desayuno Tradicional',
        'descripcion': 'Desayuno tradicional por persona.',
        'precio_unitario': Decimal('25000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
    {
        'nombre': 'Desayuno Campesino',
        'descripcion': 'Desayuno campesino por persona.',
        'precio_unitario': Decimal('25000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
    # Refrigerios
    {
        'nombre': 'Refrigerio Básico',
        'descripcion': 'Refrigerio básico por persona.',
        'precio_unitario': Decimal('12000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
    {
        'nombre': 'Refrigerio Intermedio',
        'descripcion': 'Refrigerio intermedio por persona.',
        'precio_unitario': Decimal('14000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
    {
        'nombre': 'Refrigerio Premium',
        'descripcion': 'Refrigerio premium por persona.',
        'precio_unitario': Decimal('20000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
    # Estación de Tinto
    {
        'nombre': 'Estación de Tinto',
        'descripcion': 'Estación de tinto por persona. Precio por persona y por reposición según duración.',
        'precio_unitario': Decimal('3000.00'),
        'unidad_medida': 'Persona',
        'activo': True,
    },
]

created = []
updated = []
for s in SERVICIOS:
    obj, created_flag = ServicioAdicional.objects.update_or_create(
        nombre=s['nombre'],
        defaults={
            'descripcion': s['descripcion'],
            'precio_unitario': s['precio_unitario'],
            'unidad_medida': s['unidad_medida'],
            'activo': s['activo'],
        }
    )
    if created_flag:
        created.append(obj.nombre)
    else:
        updated.append(obj.nombre)

print('Servicios creados:', created)
print('Servicios actualizados:', updated)
print('Operación finalizada.')
