import graphene
from bank.models import Payment
from bank.schema.nodes import PaymentPaginatedNode
from django.utils.translation import gettext as _
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import from_global_id
from utils.utils import get_paginator


class Query(graphene.ObjectType):
    payment = graphene.Field('bank.schema.nodes.PaymentNode', id=graphene.ID())
    all_payments = graphene.Field(
        'bank.schema.nodes.PaymentPaginatedNode', page=graphene.Int())

    my_payments = DjangoFilterConnectionField('bank.schema.nodes.PaymentNode')

    def resolve_payment(self, info, **kwargs):
        if not kwargs.get('id'):
            return None
        id = kwargs.get('id')
        global_id = from_global_id(id)[1]
        return Payment.objects.get(id=global_id)

    def resolve_all_payments(self, info, page):
        page_size = 10
        qs = Payment.objects.all()
        return get_paginator(qs, page_size, page, PaymentPaginatedNode)

    def resolve_my_payments(self, info, **kwargs):
        if info.context.user.is_anonymous:
            raise GraphQLError(_('Unauthenticated'))

        return Payment.objects.filter(user=info.context.user)
