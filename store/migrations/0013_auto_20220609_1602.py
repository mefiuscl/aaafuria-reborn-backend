# Generated by Django 3.2.13 on 2022-06-09 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_auto_20220605_2257'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='delivered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='delivered',
            field=models.BooleanField(default=False),
        ),
    ]
