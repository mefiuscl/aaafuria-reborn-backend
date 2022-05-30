import graphene
from graphene_django.filter import DjangoFilterConnectionField


class Query(graphene.ObjectType):
    all_memberships = DjangoFilterConnectionField(
        'memberships.schema.nodes.MembershipNode')
    all_membership_plans = DjangoFilterConnectionField(
        'memberships.schema.nodes.MembershipPlanNode')
