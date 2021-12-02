import stripe
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from stripe.api_resources import checkout
from django.conf import settings

"""
  Model called Socio representing a profile of each User.
"""

stripe.api_key = settings.STRIPE_API_KEY


class Socio(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    matricula = models.CharField(max_length=8, default="00000000")
    nome = models.CharField(max_length=100)
    email = models.CharField(max_length=100, null=True, blank=True)
    apelido = models.CharField(max_length=100, null=True, blank=True)
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    whatsapp = models.CharField(max_length=25, null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    rg = models.CharField(max_length=20, null=True, blank=True)
    is_socio = models.BooleanField(default=False)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    stripe_customer_id = models.CharField(max_length=50, null=True, blank=True)
    stripe_subscription_id = models.CharField(
        max_length=250, null=True, blank=True)
    stripe_portal_url = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.apelido or self.nome

    # Method that returns the active plano of the Socio.
    def get_active_plano(self):
        plano = self.planos.filter(ativo=True).first()
        if plano.is_active():
            return plano

    def create_stripe_customer(self, *args, **kwargs):
        if not self.stripe_customer_id:
            customer = stripe.Customer.create(
                name=self.nome,
                email=self.user.email,
                phone=self.whatsapp,
            )
            self.stripe_customer_id = customer.id

    def delete_stripe_customer(self, *args, **kwargs):
        try:
            customer = stripe.Customer.retrieve(self.stripe_customer_id)
            customer.delete()
        except Exception as e:
            pass

    def create_stripe_portal_url(self, *args, **kwargs):
        session = stripe.billing_portal.Session.create(
            customer=self.stripe_customer_id,
            return_url="https://aaafuria.site/areasocio",
            locale='pt-BR'
        )
        self.stripe_portal_url = session.url

    # Method that check if the subscription is active.
    def check_stripe_subscription(self):
        if self.stripe_subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(
                    self.stripe_subscription_id)

                if subscription.status == 'active':
                    self.is_socio = True
                    return True
                else:
                    self.is_socio = False
                    return False

            except Exception as e:
                return False
        return False

    def save(self, *args, **kwargs):
        self.nome = self.nome.upper()
        self.email = self.user.email.lower()

        if self.matricula == "00000000":
            self.matricula = self.user.username

        self.create_stripe_customer()

        super().save(*args, **kwargs)

    # Method that before deleting a Socio, deletes the Stripe customer.
    def delete(self, *args, **kwargs):
        self.delete_stripe_customer()
        super().delete(*args, **kwargs)


"""
  Model called Pagamento representing a payment of each Socio.
"""


class Pagamento(models.Model):
    socio = models.ForeignKey(
        Socio, on_delete=models.CASCADE, related_name='pagamentos')
    tipo_plano = models.ForeignKey('core.TipoPlano', on_delete=models.CASCADE)
    checkout_id = models.CharField(
        max_length=100, null=True, blank=True)
    checkout_url = models.CharField(max_length=400, null=True, blank=True)

    data_pagamento = models.DateField(default=timezone.now)

    status = models.CharField(
        max_length=15, default='Pendente')

    def __str__(self):
        return self.socio.nome

    def create_stripe_checkout(self, *args, **kwargs):
        checkout_session = stripe.checkout.Session.create(
            customer=self.socio.stripe_customer_id,
            success_url="https://aaafuria.site/areasocio",
            cancel_url="https://aaafuria.site/",
            line_items=[
                {
                    'price': f'{self.tipo_plano.stripe_price_id}',
                    'quantity': 1,
                },
            ],
            mode='subscription',
        )
        self.checkout_url = checkout_session.url
        self.checkout_id = checkout_session.id

    def check_status(self, *args, **kwargs):
        try:
            checkout = stripe.checkout.Session.retrieve(self.checkout_id)
            self.status = checkout.status
            if self.status == 'complete':
                self.socio.is_active = True
        except Exception as e:
            self.status = 'Cancelado'

    def save(self, *args, **kwargs):
        if not self.checkout_id:
            self.create_stripe_checkout()
        super().save(*args, **kwargs)


# Class named TipoPlano that represents the type of plan.
class TipoPlano(models.Model):
    nome = models.CharField(max_length=100)
    stripe_price_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nome
