import graphene
from graphene_django import DjangoObjectType

from .models import Conta


class ContaRelay(DjangoObjectType):

    class Meta:
        model = Conta
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    conta = graphene.relay.Node.Field(ContaRelay)
