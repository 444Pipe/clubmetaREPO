"""Alter ImagenComunicado.imagen to use CloudinaryField.

Created manually so migrations can be applied during deploy. This migration
alters the field type from ImageField to CloudinaryField. It depends on the
previous migration chain.
"""
from django.db import migrations

import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ("reservas", "0022_create_comunicado_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imagencomunicado",
            name="imagen",
            field=cloudinary.models.CloudinaryField("imagen"),
        ),
    ]
