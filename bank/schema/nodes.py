import graphene
from bank.models import Attachment, Payment
from graphene_django import DjangoObjectType


class PaymentNode(DjangoObjectType):
    method = graphene.String()

    class Meta:
        model = Payment
        interfaces = (graphene.relay.Node, )
        filter_fields = ['status']

    def resolve_method(self, info):
        return self.get_method_display()


class AttachmentNode(DjangoObjectType):
    class Meta:
        model = Attachment
        interfaces = (graphene.relay.Node, )
        filter_fields = []

    def resolve_file(self, info, *args, **kwargs):
        return info.context.build_absolute_uri(self.file.url)
