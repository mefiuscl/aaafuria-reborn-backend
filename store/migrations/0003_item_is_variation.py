# Generated by Django 3.2.12 on 2022-06-05 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_item_has_variations'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_variation',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
