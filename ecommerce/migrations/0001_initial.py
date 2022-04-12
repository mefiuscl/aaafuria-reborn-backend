# Generated by Django 3.2.12 on 2022-04-12 19:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Carrinho',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.DecimalField(
                    decimal_places=2, default=0, max_digits=8)),
                ('stripe_checkout_id', models.CharField(
                    blank=True, max_length=150, null=True)),
                ('stripe_short_checkout_url', models.CharField(
                    blank=True, max_length=400, null=True)),
                ('data_pedido', models.DateTimeField(auto_now_add=True)),
                ('data_pago', models.DateTimeField(blank=True, null=True)),
                ('data_entrega', models.DateTimeField(blank=True, null=True)),
                ('data_cancelado', models.DateTimeField(blank=True, null=True)),
                ('ordered', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('criado', 'Criado'), ('aguardando', 'Aguardando pagamento'), (
                    'pago', 'Pago'), ('entregue', 'Entregue'), ('cancelado', 'Cancelado')], default='criado', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(
                    max_length=100, verbose_name='nome do produto')),
                ('descricao', models.TextField(blank=True)),
                ('preco', models.DecimalField(decimal_places=2, max_digits=8)),
                ('preco_socio', models.DecimalField(
                    decimal_places=2, max_digits=8)),
                ('estoque', models.IntegerField(default=0)),
                ('imagem', models.ImageField(upload_to='produtos/')),
                ('has_variations', models.BooleanField(default=False)),
                ('is_hidden', models.BooleanField(default=False)),
                ('preco_staff', models.DecimalField(decimal_places=2,
                 default=0, max_digits=8, verbose_name='preço diretor')),
                ('has_observacoes', models.BooleanField(default=False)),
                ('preco_atleta', models.DecimalField(
                    decimal_places=2, max_digits=8)),
                ('exclusivo_competidor', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='VariacaoProduto',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='variação')),
                ('preco', models.DecimalField(blank=True,
                 decimal_places=2, max_digits=8, null=True)),
                ('preco_socio', models.DecimalField(blank=True,
                 decimal_places=2, max_digits=8, null=True)),
                ('estoque', models.IntegerField(default=0)),
                ('imagem', models.ImageField(blank=True,
                 null=True, upload_to='produtos/variacoes/')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='variacoes', to='ecommerce.produto')),
                ('preco_staff', models.DecimalField(blank=True, decimal_places=2,
                 max_digits=8, null=True, verbose_name='preço diretor')),
                ('preco_atleta', models.DecimalField(
                    blank=True, decimal_places=2, max_digits=8, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProdutoPedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.IntegerField(default=1)),
                ('total', models.DecimalField(
                    decimal_places=2, default=0, max_digits=8)),
                ('preco', models.DecimalField(
                    decimal_places=2, default=0, max_digits=8)),
                ('preco_socio', models.DecimalField(
                    decimal_places=2, default=0, max_digits=8)),
                ('ordered', models.BooleanField(default=False)),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='produtos', to='ecommerce.produto')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('variacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                 related_name='variacoes', to='ecommerce.variacaoproduto')),
                ('preco_staff', models.DecimalField(
                    decimal_places=2, default=0, max_digits=8)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('preco_atleta', models.DecimalField(
                    decimal_places=2, default=0, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='Pagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(
                    decimal_places=2, default=0, max_digits=8)),
                ('data_pagamento', models.DateTimeField(auto_now_add=True)),
                ('forma_pagamento', models.CharField(choices=[('cartao', 'Cartão de crédito'), (
                    'especie', 'Espécie'), ('pix', 'PIX')], default='cartao', max_length=20)),
                ('status', models.CharField(choices=[('criado', 'Criado'), ('aguardando', 'Aguardando pagamento'), (
                    'pago', 'Pago'), ('cancelado', 'Cancelado')], default='criado', max_length=20)),
                ('carrinho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='pagamentos', to='ecommerce.carrinho')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='carrinho',
            name='produtos',
            field=models.ManyToManyField(
                blank=True, to='ecommerce.ProdutoPedido'),
        ),
        migrations.AddField(
            model_name='carrinho',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
