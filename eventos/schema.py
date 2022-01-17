import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Evento, Ingresso, Lote, Participante
from graphql_relay.node.node import from_global_id


class EventoRelay(DjangoObjectType):
    class Meta:
        model = Evento
        filter_fields = ''
        interfaces = (graphene.relay.Node, )

    def resolve_imagem(self, info, *args, **kwargs):
        return info.context.build_absolute_uri(self.imagem.url)


class IngressoRelay(DjangoObjectType):
    stripe_checkout_url = graphene.String(source='stripe_checkout_url')

    class Meta:
        model = Ingresso
        filter_fields = '__all__'
        interfaces = (graphene.relay.Node, )


class LoteRelay(DjangoObjectType):
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
        participante.save()

        ingresso, _ = Ingresso.objects.get_or_create(
            lote=Lote.objects.get(id=from_global_id(lote_id)[1]),
            participante=participante,
        )
        ingresso.create_stripe_checkout()
        ingresso.save()

        return NovoIngresso(ok=True, ingresso=ingresso)


class Query(graphene.ObjectType):
    evento = graphene.relay.Node.Field(EventoRelay)
    all_evento = DjangoFilterConnectionField(EventoRelay)

    all_lote = DjangoFilterConnectionField(LoteRelay)
