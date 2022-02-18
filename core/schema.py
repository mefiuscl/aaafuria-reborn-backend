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
    stripe_portal_url = graphene.String(source='stripe_portal_url')

    class Meta:
        model = Socio
        filter_fields = ['nome', 'cpf', 'user__username']

    def resolve_avatar(self, info, *args, **kwargs):
        return info.context.build_absolute_uri(self.avatar.url)


class PagamentoType(DjangoObjectType):
    checkout_url = graphene.String(source='checkout_url')

    class Meta:
        model = Pagamento


class SocioRelay(DjangoObjectType):
    stripe_portal_url = graphene.String(source='stripe_portal_url')

    class Meta:
        model = Socio
        filter_fields = ['nome', 'cpf', 'user__username']
        interfaces = (graphene.relay.Node, )

    def resolve_avatar(self, info, *args, **kwargs):
        return info.context.build_absolute_uri(self.avatar.url)


class NovoUser(graphene.Mutation):
    class Arguments:
        matricula = graphene.String(required=True)
        turma = graphene.String(required=True)
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

    def mutate(self, info, matricula, turma, pin, email, nome, apelido, cpf, rg, data_nascimento, whatsapp):
        if matricula == '' or turma == '' or pin == '' or email == '' or nome == '' or apelido == '' or cpf == '' or rg == '' or data_nascimento == '' or whatsapp == '':
            raise Exception('Todos os campos são obrigatórios.')
        if matricula == '00000000':
            raise Exception('Matrícula inválida.')
        if len(matricula) != 8:
            raise Exception('Matrícula inválida.')
        if len(pin) != 6:
            raise Exception('PIN inválido.')

        if User.objects.filter(username=matricula).exists():
            raise Exception('Matrícula já cadastrada.')
        if User.objects.filter(email=email).exists():
            raise Exception('Email já cadastrado.')

        user = User.objects.create_user(
            username=matricula, password=pin, email=email)
        user.save()
        socio = Socio(user=user, turma=turma, nome=nome, cpf=cpf,
                      data_nascimento=data_nascimento, whatsapp=whatsapp, rg=rg, apelido=apelido)
        socio.save()

        context = {
            'socio': socio,
        }

        socio.notificar('email', 'Bem vind@ à plataforma de sócios @aaafuria!',
                        'novo_user.txt', 'novo_user.html', context)
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


class Query(graphene.ObjectType):
    socio = graphene.relay.Node.Field(SocioRelay)
    socio_autenticado = graphene.Field(SocioRelay)
    socio_by_matricula = graphene.Field(
        SocioRelay, matricula=graphene.String(required=False))
    all_socio = DjangoFilterConnectionField(SocioRelay)

    query_stripe_portal_url = graphene.Field(SocioRelay)

    def resolve_socio_autenticado(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')

        try:
            socio = Socio.objects.get(user=info.context.user)
            return socio
        except Socio.DoesNotExist:
            return Exception('Não encontrado.')

    def resolve_socio_by_matricula(self, info, matricula=None):
        if matricula:
            try:
                return Socio.objects.get(user__username=matricula)
            except Socio.DoesNotExist:
                return Exception('Matrícula não encontrada.')
            except Exception as e:
                return Exception(e)

    def resolve_query_stripe_portal_url(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')

        try:
            return Socio.objects.get(user=info.context.user)
        except Socio.DoesNotExist:
            return Exception('Sócio não encontrado.')
