from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0018_alter_configuracionsalon_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionsalon',
            name='salon_ancho',
            field=models.DecimalField(blank=True, help_text='Ancho del salón en metros', max_digits=6, decimal_places=2, null=True),
        ),
        migrations.AddField(
            model_name='configuracionsalon',
            name='salon_largo',
            field=models.DecimalField(blank=True, help_text='Largo del salón en metros', max_digits=6, decimal_places=2, null=True),
        ),
        migrations.AddField(
            model_name='configuracionsalon',
            name='salon_altura',
            field=models.DecimalField(blank=True, help_text='Altura del salón en metros', max_digits=6, decimal_places=2, null=True),
        ),
        migrations.AddField(
            model_name='configuracionsalon',
            name='tarima_ancho',
            field=models.DecimalField(blank=True, help_text='Ancho de la tarima en metros', max_digits=6, decimal_places=2, null=True),
        ),
        migrations.AddField(
            model_name='configuracionsalon',
            name='tarima_largo',
            field=models.DecimalField(blank=True, help_text='Largo de la tarima en metros', max_digits=6, decimal_places=2, null=True),
        ),
        migrations.AddField(
            model_name='configuracionsalon',
            name='tarima_altura',
            field=models.DecimalField(blank=True, help_text='Altura de la tarima en metros', max_digits=6, decimal_places=2, null=True),
        ),
        migrations.AddField(
            model_name='configuracionsalon',
            name='caracteristicas',
            field=models.TextField(blank=True, help_text='Características y servicios incluidos para esta configuración', null=True),
        ),
    ]
