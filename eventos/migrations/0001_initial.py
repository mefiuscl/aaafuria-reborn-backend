# Generated by Django 3.2.10 on 2022-01-17 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('imagem', models.ImageField(blank=True, null=True, upload_to='eventos/')),
                ('data_inicio', models.DateField()),
                ('data_fim', models.DateField()),
                ('fechado', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Participante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('whatsapp', models.CharField(blank=True, max_length=25, null=True)),
                ('rg', models.CharField(blank=True, max_length=50, null=True)),
                ('cpf', models.CharField(blank=True, max_length=11, null=True)),
                ('data_nascimento', models.DateField(blank=True, null=True)),
                ('categoria', models.CharField(choices=[('socio', 'Sócio'), ('n_socio', 'Não sócio'), ('convidado', 'Convidado'), ('organizador', 'Organizador')], default='n_socio', max_length=12)),
                ('stripe_customer_id', models.CharField(blank=True, max_length=50, null=True)),
                ('socio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.socio')),
            ],
        ),
        migrations.CreateModel(
            name='Lote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('preco', models.DecimalField(decimal_places=2, max_digits=7)),
                ('preco_socio', models.DecimalField(decimal_places=2, max_digits=7)),
                ('preco_convidado', models.DecimalField(decimal_places=2, max_digits=7)),
                ('quantidade_restante', models.IntegerField()),
                ('data_inicio', models.DateField()),
                ('data_fim', models.DateField()),
                ('ativo', models.BooleanField(default=True)),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lotes', to='eventos.evento')),
            ],
        ),
        migrations.CreateModel(
            name='Ingresso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_compra', models.DateField(auto_now_add=True)),
                ('valor', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('status', models.CharField(choices=[('pago', 'Pago'), ('aguardando', 'Aguradando pagamento'), ('pendente', 'Pendente'), ('cancelado', 'Cancelado')], default='pendente', max_length=12)),
                ('stripe_checkout_id', models.CharField(blank=True, max_length=150)),
                ('lote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventos.lote')),
                ('participante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventos.participante')),
            ],
        ),
        migrations.AddField(
            model_name='evento',
            name='participantes',
            field=models.ManyToManyField(blank=True, to='eventos.Participante'),
        ),
        migrations.CreateModel(
            name='Convidado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('aprovado', models.BooleanField(default=False)),
                ('participante_responsavel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventos.participante')),
            ],
        ),
    ]
