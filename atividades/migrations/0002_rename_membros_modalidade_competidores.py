# Generated by Django 3.2.10 on 2021-12-13 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='modalidade',
            old_name='membros',
            new_name='competidores',
        ),
    ]