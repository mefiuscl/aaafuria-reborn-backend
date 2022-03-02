import requests
import graphene
from core.models import Socio
from decouple import config
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.utils import timezone

from .models import Conta, Movimentacao, Resgate


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


class ResgatarIntermed(graphene.Mutation):
    class Arguments:
        pass

    ok = graphene.Boolean()

    def mutate(self, info):
        conta = Conta.objects.get(socio__user=info.context.user)
        socio: Socio = conta.socio

        if socio.is_socio and socio.data_fim:
            resgate, _ = Resgate.objects.get_or_create(
                conta=conta,
                descricao='Resgate desconto Intermed',
                valor_calangos=900,
            )
            resgate.resolver()

            requests.post(
                url='https://cheersshop.com.br/socio/adicionar',
                data={
                    "nome": socio.nome,
                    "email": socio.email,
                    "telefone": socio.whatsapp,
                    "matricula": socio.matricula,
                    "observacao": "",
                    "cpf": socio.cpf,
                    "data_fim_plano": socio.data_fim,
                    "vendedor": "1874"
                },
                headers={
                    "Authorization": f"Bearer {config('CHEERS_TOKEN')}",
                }
            )

            return ResgatarIntermed(ok=True)
        else:
            return ResgatarIntermed(ok=False)


class Query(graphene.ObjectType):
    conta = graphene.relay.Node.Field(ContaRelay)
    all_user_movimentacoes = DjangoFilterConnectionField(MovimentacaoRelay)

    def resolve_conta(self, info, *args, **kwargs):
        if not info.context.user.is_authenticated:
            raise Exception('Não autorizado!')

        return info.context.user.socio.conta

    def resolve_all_user_movimentacoes(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise Exception('Não autorizado!')

        return Movimentacao.objects.filter(
            conta_origem=info.context.user.socio.conta)


class Mutation(graphene.ObjectType):
    resgatar_intermed = ResgatarIntermed.Field()
