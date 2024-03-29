import graphene
from bank.models import Conta
from core.models import Socio
from django.utils import timezone
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import from_global_id

from .models import Evento, Ingresso, Lote, Participante


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
        presencial = graphene.Boolean(required=False)

    ok = graphene.Boolean()
    ingresso = graphene.Field(IngressoRelay)

    def mutate(self, info, lote_id, presencial=False):
        if not info.context.user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))

        participante, _ = Participante.objects.get_or_create(
            socio=info.context.user.socio
        )
        participante.save()

        lote = Lote.objects.get(id=from_global_id(lote_id)[1])

        if lote.is_gratuito:
            ingresso, created = Ingresso.objects.get_or_create(
                lote=lote,
                participante=participante,
            )
            if not created:
                return NovoIngresso(ok=False)

            ingresso.validate_lote()
            ingresso.set_paid()
            ingresso.save()
            return NovoIngresso(ok=True)
        else:
            ingresso, _ = Ingresso.objects.get_or_create(
                lote=lote,
                participante=participante,
            )
            ingresso.validate_lote()
            ingresso.check_quantidade()
            if not presencial:
                ingresso.create_stripe_checkout()
            ingresso.save()

            return NovoIngresso(ok=True, ingresso=ingresso)


class TransferIngresso(graphene.Mutation):
    class Arguments:
        ingresso_id = graphene.ID(required=True)
        new_owner_matricula = graphene.String(required=True)

    ok = graphene.Boolean()
    ingresso = graphene.Field(IngressoRelay)

    def mutate(self, info, ingresso_id, new_owner_matricula):
        ingresso_transfer_cost = 90  # C$
        socio_authenticated = info.context.user.socio

        if not info.context.user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))

        try:
            new_owner = Socio.objects.get(matricula=new_owner_matricula)
            ingresso = Ingresso.objects.get(id=from_global_id(ingresso_id)[1])
            previous_owner = Participante.objects.get(
                socio=ingresso.participante.socio)
        except Socio.DoesNotExist:
            raise GraphQLError(_('Sócio not found.'))
        except Participante.DoesNotExist:
            raise GraphQLError(_('Participante not found.'))
        except Ingresso.DoesNotExist:
            raise GraphQLError(_('Ingresso not found.'))

        new_owner, created = Participante.objects.get_or_create(
            socio=new_owner
        )

        if previous_owner == new_owner:
            raise GraphQLError(
                _('You cannot transfer an ingresso to yourself.'))

        if socio_authenticated.is_socio:

            conta, created = Conta.objects.get_or_create(
                socio=socio_authenticated)

            ingresso.transfers.create(
                ingresso=self,
                previous_owner=previous_owner,
                current_owner=new_owner,
                transfer_date=timezone.now())

            if conta.calangos >= ingresso_transfer_cost:
                conta.calangos -= ingresso_transfer_cost
                conta.save()
            else:
                raise GraphQLError(_('Not enough Calangos.'))

            ingresso.transfer(new_owner)
            return TransferIngresso(ok=True, ingresso=ingresso)
        else:
            raise GraphQLError(_('Not a Sócio.'))


class InvalidarIngresso(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))

        if not info.context.user.is_staff:
            raise GraphQLError(
                _('Unauthorized. Only staff members can invalidate ingressos.'))

        try:
            ingresso = Ingresso.objects.get(id=from_global_id(id)[1])
            ingresso.set_invalido()
            ingresso.save()

            return InvalidarIngresso(ok=True)
        except Ingresso.DoesNotExist:
            raise GraphQLError(_('Ingresso not found.'))
        except Exception as e:
            return GraphQLError(e)


class Query(graphene.ObjectType):
    ingresso_by_id = graphene.Field(IngressoType, id=graphene.ID())
    evento = graphene.relay.Node.Field(EventoRelay)
    all_evento = DjangoFilterConnectionField(EventoRelay)
    all_ingresso = DjangoFilterConnectionField(IngressoRelay)

    user_authenticated_ingressos = graphene.List(IngressoRelay)

    all_lote = DjangoFilterConnectionField(LoteRelay)

    def resolve_ingresso_by_id(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))

        if not info.context.user.is_staff:
            raise GraphQLError(
                _('Unauthorized. Only staff members can access ingressos.'))
        try:
            ingresso = Ingresso.objects.get(id=from_global_id(id)[1])

            return ingresso

        except Ingresso.DoesNotExist:
            raise GraphQLError(_('Ingresso not found.'))

    def resolve_all_ingresso(self, info):
        if not info.context.user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))

        if not info.context.user.is_staff:
            raise GraphQLError(
                _('Unauthorized. Only staff members can access ingressos.'))
        try:
            return Ingresso.objects.all()

        except Ingresso.DoesNotExist:
            raise GraphQLError(_('Ingresso not found.'))

    def resolve_user_authenticated_ingressos(self, info):
        if not info.context.user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))

        return Ingresso.objects.filter(participante__socio=info.context.user.socio, status='pago')


class Mutation(graphene.ObjectType):
    novo_ingresso = NovoIngresso.Field()
    invalidar_ingresso = InvalidarIngresso.Field()
    transfer_ingresso = TransferIngresso.Field()
