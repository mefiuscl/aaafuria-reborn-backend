# Generated by Django 3.2.12 on 2022-04-11 13:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0003_alter_ingressotransfer_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngressoTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_date', models.DateTimeField(blank=True, null=True)),
                ('current_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='ingressos_recebidos', to='eventos.participante')),
                ('ingresso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='transferências', to='eventos.ingresso')),
                ('previous_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='ingressos_transferidos', to='eventos.participante')),
            ],
            options={
                'verbose_name': 'transferência de ingresso',
                'verbose_name_plural': 'transferências de ingressos',
            },
        ),
    ]
