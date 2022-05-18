import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from partnerships.models import Partnership


class PartnershipRelay(DjangoObjectType):
    class Meta:
        model = Partnership
        filter_fields = ['name']
        interfaces = [relay.Node]

    def resolve_logo(self, info):
        return info.context.build_absolute_uri(self.logo.url) if self.logo else None


class Query(graphene.ObjectType):
    partnerships = graphene.List(PartnershipRelay)
    all_partnerships = DjangoFilterConnectionField(PartnershipRelay)

    def resolve_partnerships(self, info):
        return Partnership.objects.all()
