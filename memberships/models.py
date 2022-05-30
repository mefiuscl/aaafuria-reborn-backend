from django.conf import settings
from django.db import models

API_KEY = settings.STRIPE_API_KEY


class Membership(models.Model):
    ref = models.CharField(max_length=100)
    ref_id = models.CharField(max_length=255, blank=True, null=True)
    member = models.ForeignKey(
        'members.Member', on_delete=models.CASCADE, related_name='memberships')
    membership_plan = models.ForeignKey(
        'memberships.MembershipPlan', on_delete=models.CASCADE, related_name='memberships')
    payment = models.ForeignKey('bank.Payment', on_delete=models.SET_NULL,
                                related_name='memberships', blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    current_start_date = models.DateField(blank=True, null=True)
    current_end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def refresh(self):
        def refetch_stripe():
            import stripe
            stripe.api_base = API_KEY

            subscription_id = self.attachments.filter(
                title='stripe_subscription_id').first().content

            subscription = stripe.Subscription.retrieve(
                subscription_id)

            self.ref_id = subscription.id
            self.start_date = subscription.start_date
            self.end_date = subscription.end_date
            self.current_start_date = subscription.current_period_start
            self.current_end_date = subscription.current_period_end
            self.is_active = subscription.status == 'active'
            self.save()

        refs = {
            'STRIPE': refetch_stripe
        }

        return refs[self.ref]()


class Attachment(models.Model):
    membership = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=255, editable=False)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to='memberships/attachments/', blank=True, null=True)

    def __str__(self) -> str:
        return self.title


class MembershipPlan(models.Model):
    ref = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
