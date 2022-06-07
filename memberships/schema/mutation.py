import graphene
from bank.models import Payment, PaymentMethod
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from graphql_relay import from_global_id
from memberships.models import Membership, MembershipPlan


class CheckoutMembership(graphene.Mutation):
    class Arguments:
        membership_id = graphene.ID(required=True)
        method_id = graphene.String(required=True)
        user_username = graphene.String()

    ok = graphene.Boolean()
    checkout_url = graphene.String()

    def mutate(self, info, membership_id, method_id, user_username=None):
        user = info.context.user

        if user_username and user.is_staff:
            user = User.objects.get(username=user_username)

        membership_plan = MembershipPlan.objects.get(
            pk=from_global_id(membership_id)[1])

        payment_method = PaymentMethod.objects.get(
            pk=from_global_id(method_id)[1])

        payment = Payment.objects.create(
            user=user,
            description=_('Subscription creation'),
            method=payment_method,
            amount=membership_plan.price,
        )

        Membership.objects.create(
            ref=payment_method.title,
            member=user.member,
            membership_plan=membership_plan,
            payment=payment,
        )

        checkout = payment.checkout(
            mode='subscription',
            items=[
                {
                    'price': f'{membership_plan.ref}',
                    'quantity': 1,
                },
            ],
            discounts=[
                {} if user.member.memberships.all().count() > 0 else {
                    'coupon': 'PRIMEIRAASSOCIACAO'
                }
            ]
        )

        ok = True
        return CheckoutMembership(ok=ok, checkout_url=checkout['url'])


class Mutation(graphene.ObjectType):
    checkout_membership = CheckoutMembership.Field()
