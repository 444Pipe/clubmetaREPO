"""Auto-generated migration to add ImagenComunicado model.

This file was created manually because `manage.py makemigrations` could not
be executed in the current environment (DB connection parameters prevented
running makemigrations). The migration content matches the `ImagenComunicado`
model defined in `reservas/models.py`.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservas", "0020_add_salon_measurements"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImagenComunicado",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("imagen", models.ImageField(upload_to="comunicados/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Imagen Comunicado",
                "verbose_name_plural": "Imágenes Comunicados",
                "ordering": ["-uploaded_at"],
            },
        ),
    ]
