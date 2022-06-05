from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext as _


class Item(models.Model):
    ref_item = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='variations',
    )
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    membership_price = models.FloatField(blank=True, null=True)
    staff_price = models.FloatField(blank=True, null=True)
    image = models.ImageField(
        upload_to='store/images/items', blank=True, null=True)
    stock = models.IntegerField(default=0)
    has_variations = models.BooleanField(
        default=False, help_text=_('By checking this box, size variations will be created this item.'))

    is_digital = models.BooleanField(
        default=True, help_text=_('Should this item be sold online?'))
    is_analog = models.BooleanField(
        default=True, help_text=_('Should this item be sold in person?'))
    is_active = models.BooleanField(default=True)

    @property
    def is_digital_only(self):
        return self.is_digital and not self.is_analog

    @property
    def is_analog_only(self):
        return self.is_analog and not self.is_digital

    @property
    def is_variation(self):
        return self.ref_item is not None

    @property
    def is_available(self):
        return self.stock > 0

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.membership_price:
            attach, created = self.attachments.get_or_create(
                title='membership_price')
            attach.content = self.membership_price
            attach.save()
        if self.staff_price:
            attach, created = self.attachments.get_or_create(
                title='staff_price')
            attach.content = self.staff_price
            attach.save()

        if self.stock:
            attach, created = self.attachments.get_or_create(
                title='stock')
            attach.content = self.stock
            attach.save()


@receiver(models.signals.post_save, sender=Item)
def create_item_variations(sender, instance, created, **kwargs):
    if created and instance.has_variations:
        variations = [
            'PP BBLK',
            'P BBLK',
            'M BBLK',
            'G BBLK',
            'GG BBLK',
            'PP',
            'P',
            'M',
            'G',
            'GG',
        ]
        for variation in variations:
            instance.objects.create(
                item=instance,
                name=variation,
                price=instance.price,
                description=instance.description,
                membership_price=instance.membership_price,
                staff_price=instance.staff_price,
                image=instance.image,
                is_digital=instance.is_digital,
                is_analog=instance.is_analog,
                is_active=instance.is_active
            )


class Attachment(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to='store/attachments/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class CartItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.item.name} - {self.quantity}'


class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem)
    payment = models.OneToOneField(
        'bank.Payment', on_delete=models.SET_NULL, blank=True, null=True, related_name='cart')
    ordered = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.user.username} - {self.id}'

    def refresh(self):
        if self.payment.paid:
            self.ordered = True
            self.save()

    def get_total(self) -> float:
        total = 0

        for cart_item in self.items.all():
            if self.user.is_staff:
                attached_price = Attachment.objects.filter(
                    item=cart_item.item, title='staff_price').first()
                if attached_price.exists():
                    total += float(attached_price.content) * cart_item.quantity
                    continue

            if self.user.member.has_active_membership:
                attached_price = Attachment.objects.filter(
                    item=cart_item.item, title='membership_price').first()
                if attached_price.exists():
                    total += float(attached_price.content) * cart_item.quantity
                    continue

            total += cart_item.item.price * cart_item.quantity

        return total
