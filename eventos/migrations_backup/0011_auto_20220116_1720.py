# Generated by Django 3.2.10 on 2022-01-16 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0010_auto_20211227_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='participantes',
            field=models.ManyToManyField(blank=True, to='eventos.Participante'),
        ),
        migrations.AlterField(
            model_name='participante',
            name='cpf',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
        migrations.AlterField(
            model_name='participante',
            name='data_nascimento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='participante',
            name='email',
            field=models.EmailField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='participante',
            name='nome',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='participante',
            name='rg',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='participante',
            name='whatsapp',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
