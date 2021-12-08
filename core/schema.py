import graphene
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Socio, Pagamento, TipoPlano


class UserType(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = '__all__'


class SocioType(DjangoObjectType):
    class Meta:
        model = Socio
        filter_fields = ['nome', 'cpf', 'user__username']

# Object type for Socio model, named SocioType.


class PagamentoType(DjangoObjectType):
    class Meta:
        model = Pagamento


class SocioRelay(DjangoObjectType):
    class Meta:
        model = Socio
        filter_fields = ['nome', 'cpf', 'user__username']
        interfaces = (graphene.relay.Node, )


class NovoUser(graphene.Mutation):
    class Arguments:
        matricula = graphene.String(required=True)
        pin = graphene.String(required=True)
        email = graphene.String(required=True)
        nome = graphene.String(required=True)
        apelido = graphene.String(required=True)
        cpf = graphene.String(required=True)
        rg = graphene.String(required=True)
        data_nascimento = graphene.String(required=True)
        whatsapp = graphene.String(required=True)

    ok = graphene.Boolean()
    socio = graphene.Field(SocioType)

    def mutate(self, info, matricula, pin, email, nome, apelido, cpf, rg, data_nascimento, whatsapp):
        user = User.objects.create_user(
            username=matricula, password=pin, email=email)
        user.save()
        socio = Socio(user=user, nome=nome, cpf=cpf,
                      data_nascimento=data_nascimento, whatsapp=whatsapp, rg=rg, apelido=apelido)
        socio.save()
        ok = True
        return NovoUser(socio=socio, ok=ok)


class NovoPagamento(graphene.Mutation):
    class Arguments:
        tipo_plano = graphene.String(required=True)

    ok = graphene.Boolean()
    pagamento = graphene.Field(PagamentoType)

    def mutate(self, info, tipo_plano):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')

        try:
            socio = Socio.objects.get(user=info.context.user)
            pagamento = Pagamento(
                socio=socio, tipo_plano=TipoPlano.objects.get(nome=tipo_plano))
            pagamento.save()
            ok = True
            return NovoPagamento(ok=ok, pagamento=pagamento)
        except Socio.DoesNotExist:
            return Exception('Sócio não encontrado.')

# Query for the Socio model.


class Query(graphene.ObjectType):
    socio = graphene.relay.Node.Field(SocioRelay)
    socio_autenticado = graphene.Field(SocioRelay)
    socio_by_matricula = graphene.Field(
        SocioType, matricula=graphene.String(required=True))
    all_socio = DjangoFilterConnectionField(SocioRelay)

    create_portal_url = graphene.Field(SocioRelay)

    def resolve_socio_autenticado(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')

        try:
            socio = Socio.objects.get(user=info.context.user)
            return socio
        except Socio.DoesNotExist:
            return Exception('Não encontrado.')

    def resolve_socio_by_matricula(self, info, matricula):
        try:
            return Socio.objects.get(user__username=matricula)
        except Socio.DoesNotExist:
            return Exception('Matrícula não encontrada.')

    def resolve_create_portal_url(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')

        try:
            socio = Socio.objects.get(user=info.context.user)
            socio.create_stripe_portal_url()
            socio.save()
            return socio
        except Socio.DoesNotExist:
            return Exception('Sócio não encontrado.')
