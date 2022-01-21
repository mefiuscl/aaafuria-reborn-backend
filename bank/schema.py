import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Conta, Movimentacao


class MovimentacaoType(DjangoObjectType):
    class Meta:
        model = Movimentacao


class MovimentacaoRelay(DjangoObjectType):
    class Meta:
        model = Movimentacao
        interfaces = (graphene.relay.Node, )
        filter_fields = ['resolvida']


class ContaRelay(DjangoObjectType):

    class Meta:
        model = Conta
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    conta = graphene.relay.Node.Field(ContaRelay)
    all_user_movimentacoes = DjangoFilterConnectionField(MovimentacaoRelay)

    def resolve_all_user_movimentacoes(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise Exception('Não autorizado!')

        return Movimentacao.objects.filter(
            conta_origem=info.context.user.socio.conta)
