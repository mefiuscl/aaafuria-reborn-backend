import graphene
from bank.models import Payment
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id


class Query(graphene.ObjectType):
    payment = graphene.Field('bank.schema.nodes.PaymentNode', id=graphene.ID())
    all_payments = DjangoFilterConnectionField('bank.schema.nodes.PaymentNode')

    def resolve_payment(self, info, **kwargs):
        if not kwargs.get('id'):
            return None
        id = kwargs.get('id')
        global_id = from_global_id(id)[1]
        return Payment.objects.get(id=global_id)
