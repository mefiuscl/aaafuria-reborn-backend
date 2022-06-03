import graphene
from bank.models import Attachment, Payment
from graphene_django import DjangoObjectType


class PaymentNode(DjangoObjectType):
    method = graphene.String(source='get_method_display')

    class Meta:
        model = Payment
        interfaces = (graphene.relay.Node, )
        filter_fields = ['status']


class PaymentPaginatedNode(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(PaymentNode)


class AttachmentNode(DjangoObjectType):
    class Meta:
        model = Attachment
        interfaces = (graphene.relay.Node, )
        filter_fields = []

    def resolve_file(self, info, *args, **kwargs):
        return info.context.build_absolute_uri(self.file.url)
