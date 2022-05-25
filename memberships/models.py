from ast import Sub
from turtle import title

from django.db import models


def member_avatar_dir(instance, filename):
    filename = 'avatar' + '.' + filename.split('.')[-1]
    return f'members/{instance.user.username}/{filename}'


def member_attachments_dir(instance):
    return f'members/{instance.user.username}/attachments'


class Member(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)

    registration = models.CharField(max_length=8, default='00000000')
    group = models.CharField(max_length=10, default='MED: 00')

    name = models.CharField(max_length=150)
    nickname = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)

    avatar = models.ImageField(
        upload_to=member_avatar_dir, null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    rg = models.CharField(max_length=15, null=True, blank=True)


class Membership(models.Model):
    REF_CHOICES = (
        ('STRIPE', 'Stripe'),
    )
    member = models.ForeignKey(
        'memberships.Member', on_delete=models.CASCADE, related_name='memberships')
    ref_id = models.CharField(max_length=255)
    ref = models.CharField(max_length=50, choices=REF_CHOICES)
    description = models.CharField(max_length=255)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def refresh_stripe(self):
        import stripe
        from django.conf import settings
        from stripe import Subscription

        stripe.api_key = settings.STRIPE_SECRET_KEY

        subscription = Subscription.retrieve(self.ref_id)
        self.start_date = subscription.current_period_start
        self.end_date = subscription.current_period_end
        self.is_active = subscription.status == 'active'
        self.save()

    def refresh(self):
        refs = {
            'STRIPE': self.refresh_stripe,
        }
        refs[self.ref]()


class Attachment(models.Model):
    member = models.ForeignKey(
        'memberships.Member', on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=255, null=True, blank=True)
    attachment = models.FileField(upload_to=member_attachments_dir)
