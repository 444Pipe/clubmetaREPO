from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Actualizar la descripción del salón especificado con medidas y características detalladas.'

    def add_arguments(self, parser):
        parser.add_argument('--name', help='Nombre (o parte) del salón a actualizar', default='Mi llanura')

    def handle(self, *args, **options):
        name = options.get('name')
        from reservas.models import Salon

        # Texto con las medidas y características (tal como lo proporcionó el usuario)
        detalle = '''\n\nMEDIDAS SALÓN:\n- Ancho: 26.6 m\n- Largo: 23.5 m\n- Altura: 3.4 m\n\nMEDIDAS TARIMA:\n- Ancho: 5.6 m\n- Largo: 10.5 m\n- Altura: 3.0 m\n\nCARACTERÍSTICAS:\n- Espacio acondicionado para eventos sociales y empresariales.\n- El alquiler del salón incluye servicio de montaje.\n- Telón de proyección\n- Internet Wi‑Fi\n- Papelógrafo\n- Marcadores\n- Borrador\n- Aire acondicionado\n- Parqueadero\n'''

        with transaction.atomic():
            qs = Salon.objects.filter(nombre__icontains=name)
            count = qs.count()
            if count == 0:
                self.stdout.write(self.style.ERROR(f'No se encontró ningún salón con "{name}" en el nombre.'))
                return

            for salon in qs:
                original = salon.descripcion or ''
                if detalle.strip() in original:
                    self.stdout.write(self.style.WARNING(f'El salón "{salon.nombre}" ya contiene la información; se omite.'))
                    continue

                salon.descripcion = original + detalle
                salon.save()
                self.stdout.write(self.style.SUCCESS(f'Actualizado salón: {salon.nombre}'))

        self.stdout.write(self.style.SUCCESS('Proceso finalizado.'))
