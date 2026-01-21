from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0018_alter_configuracionsalon_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionsalon',
            name='imagen_montaje',
            field=models.CharField(max_length=300, blank=True, help_text='Ruta relativa en static/img/ para la imagen de este montaje'),
        ),
    ]
