import graphene
import requests
from core.models import Socio
from decouple import config
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from .models import Conta, Movimentacao, Resgate


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
        if not info.context.user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))
        conta = Conta.objects.get(socio__user=info.context.user)
        socio: Socio = conta.socio

        if socio.is_socio and socio.data_fim:
            resgate, _ = Resgate.objects.get_or_create(
                conta=conta,
                descricao='Resgate desconto Intermed',
                valor_calangos=900,
            )
            resgate.resolver()

            if resgate.resolvida:
                requests.post(
                    url='http://intermednordeste.com/api/user',
                    data={
                        "email": socio.email,
                        "password": socio.matricula,
                        "name": socio.nome,
                        "birth date": socio.data_nascimento,
                        "rg": socio.rg,
                        "cpf": socio.cpf,
                        "street": "Rua Aristides Saraiva de Almeida",
                        "number": "960",
                        "id_city": 3585,
                        "id_state": 22,
                        "id_type": 1,
                        "phone": "(86) 9 8131-2488",
                        "id_club": 9,
                        "photo": socio.avatar,
                        "vaccine_card": socio.vaccine_card,
                        "enroll": socio.declaracao_matricula,
                    }
                )

                return ResgatarIntermed(ok=True)
            else:
                return ResgatarIntermed(ok=False)
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
