import graphene
from bank.models import Payment
from graphene_django import DjangoObjectType


class PaymentNode(DjangoObjectType):
    class Meta:
        model = Payment
        interfaces = (graphene.relay.Node, )
        filter_fields = []
