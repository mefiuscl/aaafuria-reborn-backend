from django.core.exceptions import ValidationError
import stripe
from django.db import models
from django.conf import settings
from django.utils import timezone

from bank.models import Conta


class Participante(models.Model):
    socio = models.ForeignKey(
        'core.Socio', on_delete=models.CASCADE, blank=True, null=True)

    nome = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    whatsapp = models.CharField(max_length=25, blank=True, null=True)
    rg = models.CharField(max_length=50, blank=True, null=True)
    cpf = models.CharField(max_length=11, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)

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

    convites_disponiveis = models.PositiveIntegerField(default=1)

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
                self.categoria = 'n_socio'
        else:
            self.categoria = 'convidado'

        super().save(*args, **kwargs)


class Convidado(models.Model):
    participante_responsavel: Participante = models.ForeignKey(
        Participante, on_delete=models.CASCADE)
    evento: 'Evento' = models.ForeignKey(
        'eventos.Evento', on_delete=models.CASCADE, related_name='evento', blank=True, null=True)
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
    participantes: Participante = models.ManyToManyField(
        Participante, blank=True)
    convidados: Convidado = models.ManyToManyField(
        Convidado, blank=True, related_name='convidados')
    imagem = models.ImageField(
        upload_to='eventos/', null=True, blank=True)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    fechado = models.BooleanField(default=True)

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
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    @property
    def is_gratuito(self):
        if self.preco == self.preco_socio == 0:
            return True

        return False

    def update_ativo(self):
        if self.quantidade_restante < 1:
            self.ativo = False
        elif self.quantidade_restante >= 1:
            self.ativo = True

    def clean(self):
        if self.data_fim < self.data_inicio:
            raise ValidationError(
                'A data de início não pode ser maior que a data de fim')

        if self.data_inicio > self.evento.data_inicio:
            raise ValidationError(
                'A data de início não pode ser maior que a data de início do evento')

        if self.data_fim > self.evento.data_fim:
            raise ValidationError(
                'A data de fim não pode ser maior que a data de fim do evento')

    def save(self, *args, **kwargs):
        self.update_ativo()
        if self.ativo:
            for lote in self.evento.lotes.all():
                if lote.id != self.id:
                    lote.ativo = False
                    lote.save()
        self.clean()
        super().save(*args, **kwargs)


class Ingresso(models.Model):
    lote: Lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    participante: Participante = models.ForeignKey(
        Participante, on_delete=models.CASCADE)
    data_compra = models.DateTimeField(blank=True, null=True)
    valor = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    status = models.CharField(
        max_length=12,
        choices=(
            ('invalido', 'Inválido'),
            ('pago', 'Pago'),
            ('aguardando', 'Aguradando pagamento'),
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

    def set_invalido(self):
        self.status = 'invalido'

    def get_stripe_checkout_url(self, api_key=settings.STRIPE_API_TEST_KEY) -> str:
        if self.stripe_checkout_id:
            stripe.api_key = api_key
            session = stripe.checkout.Session.retrieve(self.stripe_checkout_id)

            return session.url

    def create_stripe_checkout(self, api_key=settings.STRIPE_API_TEST_KEY):
        self.set_valor()
        stripe.api_key = api_key
        session = stripe.checkout.Session.create(
            success_url='https://aaafuria.site/',
            cancel_url='https://aaafuria.site/eventos',
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
        self.status = 'aguardando'

    def set_paid(self):
        self.lote.quantidade_restante -= 1
        if self.lote.quantidade_restante < 0:
            raise ValidationError('Não há ingressos disponíveis')

        if self.participante.socio:
            conta, _ = Conta.objects.get_or_create(
                socio=self.participante.socio)
            if conta.socio.is_socio:
                conta.calangos += int(
                    (self.valor // 5) * 50)
            conta.save()

        self.status = 'pago'
        self.data_compra = timezone.now()
        self.lote.update_ativo()
        self.lote.save()

        self.lote.evento.participantes.add(self.participante)
        self.lote.evento.save()

    def save(self, *args, **kwargs):
        self.set_valor()

        super().save(*args, **kwargs)
