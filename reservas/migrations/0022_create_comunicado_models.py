"""Migration to create Comunicado and ComunicadoImagen models.

This migration was created manually to ensure the `reservas_comunicado`
and `reservas_comunicadoimagen` tables exist in the database.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservas", "0021_create_imagencomunicado"),
    ]

    operations = [
        migrations.CreateModel(
            name="Comunicado",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=255)),
                ("cuerpo", models.TextField(blank=True)),
                ("publicado", models.DateTimeField(null=True, blank=True)),
                ("activo", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Comunicado",
                "verbose_name_plural": "Comunicados",
                "ordering": ["-publicado"],
            },
        ),
        migrations.CreateModel(
            name="ComunicadoImagen",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("imagen", models.ImageField(upload_to="comunicados/%Y/%m/%d/")),
                ("orden", models.PositiveSmallIntegerField(default=0)),
                ("comunicado", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="images", to="reservas.comunicado")),
            ],
            options={
                "verbose_name": "Imagen de Comunicado",
                "verbose_name_plural": "Imágenes de Comunicados",
                "ordering": ["orden", "id"],
            },
        ),
    ]
