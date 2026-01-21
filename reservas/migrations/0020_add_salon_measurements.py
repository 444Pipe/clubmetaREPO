# Generated manually: add measurement fields to Salon
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0019_add_imagen_montaje'),
    ]

    operations = [
        migrations.AddField(
            model_name='salon',
            name='largo_m',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Largo en metros (opcional)', max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='salon',
            name='ancho_m',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Ancho en metros (opcional)', max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='salon',
            name='alto_m',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Alto en metros (opcional)', max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='salon',
            name='diametro_m',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Diámetro en metros (opcional)', max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='salon',
            name='tarima_largo_m',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Largo de la tarima en metros (opcional)', max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='salon',
            name='tarima_ancho_m',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Ancho de la tarima en metros (opcional)', max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='salon',
            name='tarima_alto_m',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Alto de la tarima en metros (opcional)', max_digits=6, null=True),
        ),
    ]
