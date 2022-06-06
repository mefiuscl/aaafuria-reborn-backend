import graphene
from bank.models import Payment
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from graphql import GraphQLError
from graphql_relay import from_global_id
from store.models import Cart, CartItem, Item


class AddToCart(graphene.Mutation):
    class Arguments:
        item_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)
        description = graphene.String()
        user_username = graphene.String()

    ok = graphene.Boolean()

    def mutate(self, info, item_id, quantity, description=None, user_username=None):
        user = info.context.user
        item = Item.objects.filter(id=from_global_id(item_id)[1]).first()

        if user.is_anonymous:
            raise GraphQLError(_('Unauthenticated'))
        if user.is_staff and user_username is not None:
            user = User.objects.filter(username=user_username).first()
        if not item:
            raise GraphQLError(_('Item not found'))
        '''
        # stock check
        if item.is_available is False:
            raise GraphQLError(_('Item is not available'))
        '''

        cart = info.context.user.carts.filter(
            checked_out=False).first()
        if not cart:
            cart = Cart.objects.create(user=user)

        cart_item, created = CartItem.objects.get_or_create(
            item_id=item.id, cart=cart, description=description, checked_out=False)

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        ok = True
        return AddToCart(ok=ok)


class RemoveFromCart(graphene.Mutation):
    class Arguments:
        item_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)
        user_username = graphene.String()

    ok = graphene.Boolean()

    def mutate(self, info, item_id, quantity, user_username=None):
        user = info.context.user
        item = Item.objects.filter(id=from_global_id(item_id)[1]).first()

        if user.is_anonymous:
            raise GraphQLError(_('Unauthenticated'))
        if user.is_staff and user_username is not None:
            user = User.objects.filter(username=user_username).first()
        if not item:
            raise GraphQLError(_('Item not found'))

        cart = info.context.user.carts.filter(
            checked_out=False).first()
        if not cart:
            raise GraphQLError(_('Cart not found'))

        cart_item = CartItem.objects.filter(
            item_id=item.id, cart=cart).first()
        if not cart_item:
            raise GraphQLError(_('Item not found in cart'))

        if cart_item.quantity <= quantity:
            cart_item.delete()
        else:
            cart_item.quantity -= quantity
            cart_item.save()

        ok = True
        return RemoveFromCart(ok=ok)


class DeleteFromCart(graphene.Mutation):
    class Arguments:
        item_id = graphene.ID(required=True)
        user_username = graphene.String()

    ok = graphene.Boolean()

    def mutate(self, info, item_id, user_username=None):
        user = info.context.user
        item = Item.objects.filter(id=from_global_id(item_id)[1]).first()

        if user.is_anonymous:
            raise GraphQLError(_('Unauthenticated'))
        if user.is_staff and user_username is not None:
            user = User.objects.filter(username=user_username).first()
        if not item:
            raise GraphQLError(_('Item not found'))

        cart = info.context.user.carts.filter(
            checked_out=False).first()
        if not cart:
            raise GraphQLError(_('Cart not found'))

        cart_item = CartItem.objects.filter(
            item_id=item.id, cart=cart).first()
        if not cart_item:
            raise GraphQLError(_('Item not found in cart'))

        cart_item.delete()

        ok = True
        return DeleteFromCart(ok=ok)


class CheckoutCart(graphene.Mutation):
    class Arguments:
        method = graphene.String(required=True)
        user_username = graphene.String()

    ok = graphene.Boolean()
    checkout_url = graphene.String()

    def mutate(self, info, method, user_username=None):
        user = info.context.user
        cart = info.context.user.carts.filter(checked_out=False).first()

        if user.is_anonymous:
            raise GraphQLError(_('Unauthenticated'))
        if user.is_staff and user_username is not None:
            user = User.objects.filter(username=user_username).first()
        if not cart:
            raise GraphQLError(_('Cart not found'))
        if cart.items.count() == 0:
            raise GraphQLError(_('Cart is empty'))

        payment = Payment.objects.create(
            user=user,
            description=_('Store checkout created'),
            method=method,
            amount=cart.get_total(),
        )

        checkout = payment.checkout(
            mode='payment',
            items=[
                {
                    'name': str(item),
                    'quantity': item.quantity,
                    'currency': 'BRL',
                    'amount': int(item.get_sub_total() * 100),
                    'tax_rates': ['txr_1KT7puH8nuTtWMpP8U05kbNZ']
                } for item in cart.items.all()
            ],
            discounts=[
                {} if info.context.user.member.memberships.all().count() > 0 else {
                    'coupon': 'PRIMEIRAASSOCIACAO'
                }
            ]
        )

        cart.checkout(payment)
        cart.refresh()
        cart.save()

        ok = True
        return CheckoutCart(ok=ok, checkout_url=checkout['url'])


class Mutation(graphene.ObjectType):
    add_to_cart = AddToCart.Field()
    remove_from_cart = RemoveFromCart.Field()
    delete_from_cart = DeleteFromCart.Field()
    checkout_cart = CheckoutCart.Field()
