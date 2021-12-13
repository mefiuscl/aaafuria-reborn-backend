# Generated by Django 3.2.10 on 2021-12-13 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0003_auto_20211213_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='programacao',
            name='competidores_maximo',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='programacao',
            name='competidores_minimo',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='programacao',
            name='estado',
            field=models.CharField(default='Agendado', max_length=10),
        ),
        migrations.AlterField(
            model_name='modalidade',
            name='categoria',
            field=models.CharField(choices=[('Diretoria', 'Diretoria'), ('Coord', 'Coordenação'), ('Esporte', 'Esporte'), ('Bateria', 'Bateria'), ('Social', 'Ação social'), ('Outra', 'Outra')], max_length=10),
        ),
        migrations.AlterField(
            model_name='modalidade',
            name='competidores',
            field=models.ManyToManyField(blank=True, related_name='modalidades', to='atividades.Competidor'),
        ),
    ]
