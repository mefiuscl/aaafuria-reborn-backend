import graphene
from bank.models import Payment
from django.utils.translation import gettext as _
from graphql_relay import from_global_id
from memberships.models import Membership, MembershipPlan


class CheckoutMembership(graphene.Mutation):
    class Arguments:
        membership_id = graphene.Int(required=True)

    ok = graphene.Boolean()
    checkout_url = graphene.String()

    def mutate(self, info, method, membership_id):
        membership_plan = MembershipPlan.objects.get(
            pk=from_global_id(membership_id)[0])

        payment = Payment.objects.create(
            description=_('Subscription creation'),
            method=method,
        )
        membership = Membership.objects.create(
            ref=method,
            member=info.context.user.member,
            plan=membership_plan,
            payment=payment,
        )

        ok = True
        checkout_url = 'https://www.google.com'
        return CheckoutMembership(ok=ok, checkout_url=checkout_url)


class Mutation(graphene.ObjectType):
    pass
