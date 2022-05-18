import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.node.node import from_global_id

from .models import Competidor, Programacao


class CompetidorRelay(DjangoObjectType):
    class Meta:
        model = Competidor
        filter_fields = '__all__'
        interfaces = (graphene.relay.Node, )


class ProgramacaoRelay(DjangoObjectType):
    finalizado = graphene.Boolean(source='finalizado')

    class Meta:
        model = Programacao
        filter_fields = ['modalidade__categoria',
                         'estado', ]
        interfaces = (graphene.relay.Node, )


class ConfirmarCompetidorNaProgramacao(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        competidor, _ = Competidor.objects.get_or_create(
            socio=info.context.user.socio)

        programacao = Programacao.objects.get(id=from_global_id(id)[1])

        if programacao.competidores_maximo != 0 and programacao.competidores_confirmados.count() >= programacao.competidores_maximo:
            raise Exception("Não é possível confirmar mais competidores")

        programacao.competidores_confirmados.add(competidor)

        competidor.save()
        programacao.save()

        programacao.checar_estado()

        return ConfirmarCompetidorNaProgramacao(ok=True)


class RemoverCompetidorNaProgramacao(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        competidor = Competidor.objects.get(
            socio=info.context.user.socio)

        programacao = Programacao.objects.get(id=from_global_id(id)[1])
        programacao.competidores_confirmados.remove(competidor)
        programacao.save()

        programacao.checar_estado()

        return RemoverCompetidorNaProgramacao(ok=True)


class Query(graphene.ObjectType):
    all_programacao = DjangoFilterConnectionField(ProgramacaoRelay)

    programacao = graphene.Field(
        ProgramacaoRelay, id=graphene.ID(required=True))

    def resolve_programacao(self, info, id, *args, **kwargs):
        return Programacao.objects.get(id=from_global_id(id)[1])

    def resolve_all_programacao(self, info, *args, **kwargs):
        return Programacao.objects.exclude(estado='Finalizado')


class Mutation(graphene.ObjectType):
    confirmar_competidor_na_programacao = ConfirmarCompetidorNaProgramacao.Field()
    remover_competidor_na_programacao = RemoverCompetidorNaProgramacao.Field()
