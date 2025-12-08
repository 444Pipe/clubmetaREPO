from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Actualizar la descripción de un salón por su nombre (nombre exacto o case-insensitive)'

    def add_arguments(self, parser):
        parser.add_argument('--nombre', '-n', type=str, help='Nombre del salón a actualizar', required=True)
        parser.add_argument('--descripcion', '-d', type=str, help='Nueva descripción (entre comillas)')

    def handle(self, *args, **options):
        nombre = options.get('nombre')
        descripcion = options.get('descripcion')

        if not nombre:
            raise CommandError('Debe especificar --nombre del salón')

        if descripcion is None:
            raise CommandError('Debe especificar --descripcion con el texto a aplicar (entre comillas)')

        from reservas.models import Salon

        qs = Salon.objects.filter(nombre__iexact=nombre)
        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING(f'No se encontró ningún salón con nombre igual a "{nombre}" (case-insensitive).'))
            return

        for salon in qs:
            salon.descripcion = descripcion
            salon.save()
            self.stdout.write(self.style.SUCCESS(f'Actualizada descripción de salón: {salon.nombre} (id={salon.id})'))

        self.stdout.write(self.style.NOTICE(f'Total actualizado: {count} sala(s)'))
