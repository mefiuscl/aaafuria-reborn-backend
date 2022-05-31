import graphene
from graphene_django import DjangoObjectType
from members.models import Member


class MemberNode(DjangoObjectType):
    first_teamer = graphene.Boolean(source='first_teamer')
    has_active_membership = graphene.Boolean(source='has_active_membership')
    active_membership = graphene.Field(
        'memberships.schema.nodes.MembershipNode', source='active_membership')

    class Meta:
        model = Member
        interfaces = (graphene.relay.Node,)
        filter_fields = []

    def resolve_avatar(self, info, *args, **kwargs):
        if self.avatar:
            return info.context.build_absolute_uri(self.avatar.url)
