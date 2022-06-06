from django.contrib import admin

from store.models import Attachment, Cart, CartItem, Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    pass


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'ordered',
        'checked_out',
        'created_at',
        'updated_at',

    ]
