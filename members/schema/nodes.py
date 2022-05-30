import graphene
from graphene_django import DjangoObjectType
from members.models import Member


class MemberNode(DjangoObjectType):
    class Meta:
        model = Member
        interfaces = (graphene.relay.Node,)
        filter_fields = []
