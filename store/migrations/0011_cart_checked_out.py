# Generated by Django 3.2.12 on 2022-06-06 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_auto_20220605_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='checked_out',
            field=models.BooleanField(default=False),
        ),
    ]
