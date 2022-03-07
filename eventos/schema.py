import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Evento, Ingresso, Lote, Participante
from graphql_relay.node.node import from_global_id
from graphql import GraphQLError


class EventoRelay(DjangoObjectType):
    class Meta:
        model = Evento
        filter_fields = ''
        interfaces = (graphene.relay.Node, )

    def resolve_imagem(self, info, *args, **kwargs):
        if self.imagem:
            return info.context.build_absolute_uri(self.imagem.url)


class ParticipanteType(DjangoObjectType):
    class Meta:
        model = Participante
        filter_fields = []


class IngressoType(DjangoObjectType):
    class Meta:
        model = Ingresso
        filter_fields = []


class IngressoRelay(DjangoObjectType):
    stripe_checkout_url = graphene.String(source='get_stripe_checkout_url')

    class Meta:
        model = Ingresso
        filter_fields = '__all__'
        interfaces = (graphene.relay.Node, )


class LoteRelay(DjangoObjectType):
    is_gratuito = graphene.Boolean(source='is_gratuito')

    class Meta:
        model = Lote
        filter_fields = ['ativo', 'evento__fechado']
        interfaces = (graphene.relay.Node, )


class NovoIngresso(graphene.Mutation):
    class Arguments:
        lote_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    ingresso = graphene.Field(IngressoRelay)

    def mutate(self, info, lote_id):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')

        participante, _ = Participante.objects.get_or_create(
            socio=info.context.user.socio
        )

        lote = Lote.objects.get(id=from_global_id(lote_id)[1])

        if lote.is_gratuito:
            ingresso, created = Ingresso.objects.get_or_create(
                lote=lote,
                participante=participante,
            )
            if not created:
                return NovoIngresso(ok=False)

            ingresso.set_paid()
            ingresso.save()
            return NovoIngresso(ok=True)
        else:
            ingresso, _ = Ingresso.objects.get_or_create(
                lote=lote,
                participante=participante,
            )

            if not created:
                return NovoIngresso(ok=False)

            ingresso.create_stripe_checkout()
            ingresso.save()

            return NovoIngresso(ok=True, ingresso=ingresso)


class InvalidarIngresso(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')

        if not info.context.user.is_staff:
            raise Exception(
                'Apenas administradores podem invalidar ingressos.')

        try:
            ingresso = Ingresso.objects.get(id=from_global_id(id)[1])
            ingresso.set_invalido()
            ingresso.save()

            return InvalidarIngresso(ok=True)
        except Ingresso.DoesNotExist:
            raise GraphQLError('Ingresso não encontrado.')


class Query(graphene.ObjectType):
    ingresso_by_id = graphene.Field(IngressoType, id=graphene.ID())
    evento = graphene.relay.Node.Field(EventoRelay)
    all_evento = DjangoFilterConnectionField(EventoRelay)
    all_ingresso = DjangoFilterConnectionField(IngressoRelay)

    user_authenticated_ingressos = graphene.List(IngressoRelay)

    all_lote = DjangoFilterConnectionField(LoteRelay)

    def resolve_ingresso_by_id(self, info, id):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')

        if not info.context.user.is_staff:
            raise Exception('Usuário não autorizado.')
        try:
            ingresso = Ingresso.objects.get(id=from_global_id(id)[1])

            return ingresso

        except Ingresso.DoesNotExist:
            raise GraphQLError('Ingresso não encontrado.')

    def resolve_all_ingresso(self, info):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')

        if not info.context.user.is_staff:
            raise Exception('Usuário não autorizado.')
        try:
            return Ingresso.objects.all()

        except Ingresso.DoesNotExist:
            raise Exception('Ingresso não encontrado.')

    def resolve_user_authenticated_ingressos(self, info):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')

        return Ingresso.objects.filter(participante__socio=info.context.user.socio, status='pago')


class Mutation(graphene.ObjectType):
    novo_ingresso = NovoIngresso.Field()
    invalidar_ingresso = InvalidarIngresso.Field()
