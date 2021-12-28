from django.core.exceptions import ValidationError
import stripe
from django.db import models
from django.conf import settings


class Participante(models.Model):
    socio = models.ForeignKey(
        'core.Socio', on_delete=models.CASCADE, blank=True, null=True)

    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    whatsapp = models.CharField(max_length=25)
    rg = models.CharField(max_length=50)
    cpf = models.CharField(max_length=11)
    data_nascimento = models.DateField()

    categoria = models.CharField(
        max_length=12,
        choices=(
            ('socio', 'Sócio'),
            ('n_socio', 'Não sócio'),
            ('convidado', 'Convidado'),
            ('organizador', 'Organizador'),
        ),
        default='n_socio',
    )

    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.socio:
            self.nome = self.socio.nome
            self.email = self.socio.user.email
            self.whatsapp = self.socio.whatsapp
            self.rg = self.socio.rg
            self.cpf = self.socio.cpf
            self.data_nascimento = self.socio.data_nascimento

            self.stripe_customer_id = self.socio.stripe_customer_id

            if self.socio.is_socio:
                self.categoria = 'socio'
        else:
            self.categoria = 'convidado'

        super().save(*args, **kwargs)


class Convidado(models.Model):
    participante_responsavel = models.ForeignKey(
        Participante, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    aprovado = models.BooleanField(default=False)

    def __str__(self):
        return self.nome

    def enviar_convite(self):
        pass

    def aprovar(self):
        self.enviar_convite()
        self.aprovado = True


class Evento(models.Model):
    nome = models.CharField(max_length=100)
    participantes = models.ManyToManyField(Participante)
    data_inicio = models.DateField()
    data_fim = models.DateField()

    def __str__(self):
        return self.nome


class Lote(models.Model):
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, related_name='lotes')
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=7, decimal_places=2)
    preco_socio = models.DecimalField(max_digits=7, decimal_places=2)
    preco_convidado = models.DecimalField(max_digits=7, decimal_places=2)
    quantidade_restante = models.IntegerField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    def clean(self):
        if self.data_fim < self.data_inicio:
            raise ValidationError(
                'A data de início não pode ser maior que a data de fim')

        if self.data_inicio < self.evento.data_inicio:
            raise ValidationError(
                'A data de início não pode ser menor que a data de início do evento')

        if self.data_fim > self.evento.data_fim:
            raise ValidationError(
                'A data de fim não pode ser maior que a data de fim do evento')

    def save(self, *args, **kwargs):
        if self.ativo:
            for lote in self.evento.lotes.all():
                if lote.id != self.id:
                    lote.ativo = False
                    lote.save()

        self.clean()
        super().save(*args, **kwargs)


class Ingresso(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    data_compra = models.DateField(auto_now_add=True)
    valor = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(
        max_length=12,
        choices=(
            ('pago', 'Pago'),
            ('pendente', 'Pendente'),
            ('cancelado', 'Cancelado'),
        ),
        default='pendente',
    )

    stripe_checkout_id = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f'{self.lote.evento.nome} - {self.lote.nome}'

    def set_valor(self):
        categoria = {
            'socio': self.lote.preco_socio,
            'n_socio': self.lote.preco,
            'convidado': self.lote.preco_convidado,
        }

        self.valor = categoria[self.participante.categoria]

    def save(self, *args, **kwargs):
        self.set_valor()
        super().save(*args, **kwargs)

    def create_stripe_checkout(self, api_key=settings.STRIPE_API_TEST_KEY):
        stripe.api_key = api_key
        session = stripe.checkout.Session.create(
            success_url='https://aaafuria.site/',
            cancel_url='https://aaafuria.site/carrinho',
            mode='payment',
            line_items=[
                {
                    'name': self.lote.evento.nome,
                    'description': f'{self.lote.nome} - {self.participante.get_categoria_display()}',
                    'quantity': 1,
                    'currency': 'BRL',
                    'amount': int(self.valor * 100),
                }
            ],
            customer=self.participante.stripe_customer_id or None,
            payment_method_types=['card'],
        )

        self.stripe_checkout_id = session.id

    def get_stripe_checkout_url(self, api_key=settings.STRIPE_API_TEST_KEY):
        stripe.api_key = api_key
        session = stripe.checkout.Session.retrieve(self.stripe_checkout_id)

        return session.url

    def set_paid(self):
        self.status = 'pago'
        self.lote.quantidade_restante -= 1
        self.lote.save()

        self.lote.evento.participantes.add(self.participante)
        self.lote.evento.save()
