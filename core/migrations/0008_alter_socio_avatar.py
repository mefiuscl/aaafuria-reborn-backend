# Generated by Django 3.2.10 on 2021-12-12 15:32

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_socio_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socio',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.avatar_dir),
        ),
    ]