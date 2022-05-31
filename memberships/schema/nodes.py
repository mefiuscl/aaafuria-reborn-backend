import graphene
from graphene_django import DjangoObjectType
from memberships.models import Membership, MembershipPlan


class MembershipNode(DjangoObjectType):
    class Meta:
        model = Membership
        interfaces = (graphene.relay.Node, )
        filter_fields = ['is_active']


class MembershipPlanNode(DjangoObjectType):
    class Meta:
        model = MembershipPlan
        interfaces = (graphene.relay.Node, )
        filter_fields = []
