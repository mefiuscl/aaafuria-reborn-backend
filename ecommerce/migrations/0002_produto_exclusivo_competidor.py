# Generated by Django 3.2.12 on 2022-03-31 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0001_initial_squashed'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='exclusivo_competidor',
            field=models.BooleanField(default=False),
        ),
    ]
