# Generated by Django 3.2.12 on 2022-03-29 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0001_initial_squashed_0002_programacao_grupo_whatsapp_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='programacao',
            name='notify',
            field=models.BooleanField(default=False),
        ),
    ]