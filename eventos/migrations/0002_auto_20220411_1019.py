# Generated by Django 3.2.12 on 2022-04-11 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0001_initial_squashed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingressotransfer',
            options={'verbose_name': 'transferência de ingresso', 'verbose_name_plural': 'transferências de ingresso'},
        ),
        migrations.AlterField(
            model_name='ingressotransfer',
            name='current_owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_ingressos', to='eventos.participante'),
        ),
        migrations.AlterField(
            model_name='ingressotransfer',
            name='ingresso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers', to='eventos.ingresso'),
        ),
        migrations.AlterField(
            model_name='ingressotransfer',
            name='previous_owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfered_ingressos', to='eventos.participante'),
        ),
    ]
