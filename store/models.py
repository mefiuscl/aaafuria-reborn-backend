from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    membership_price = models.FloatField(blank=True, null=True)
    staff_price = models.FloatField(blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(
        upload_to='store/images/items', blank=True, null=True)

    def save(self, *args, **kwargs):
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

        super().save(*args, **kwargs)


class ItemVariation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.FloatField(blank=True, null=True)
    membership_price = models.FloatField(blank=True, null=True)
    staff_price = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='store/images/items', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.item.price
        if not self.membership_price and self.item.membership_price:
            self.membership_price = self.item.membership_price
        if not self.staff_price and self.item.staff_price:
            self.staff_price = self.item.staff_price
        if not self.description and self.item.description:
            self.staff_price = self.item.description
        if not self.image and self.item.image:
            self.image = self.item.image

        super().save(*args, **kwargs)


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
