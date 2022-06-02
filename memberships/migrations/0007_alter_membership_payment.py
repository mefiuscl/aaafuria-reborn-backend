# Generated by Django 3.2.12 on 2022-05-31 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0009_auto_20220531_1017'),
        ('memberships', '0006_alter_membership_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='payment',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='memberships', to='bank.payment'),
        ),
    ]