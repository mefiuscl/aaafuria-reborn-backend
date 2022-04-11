import datetime

import graphene
from bank.models import Conta, Movimentacao
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from .models import Pagamento, Socio, TipoPlano


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


class VerifyEmail(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, email):
        if not info.context.user or not info.context.user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))
        if not email:
            raise GraphQLError(_('Email is required'))

        user = info.context.user

        if user.socio.verified_email:
            return VerifyEmail(ok=False)

        user.socio.verified_email = True

        user.email = email
        user.socio.email = email

        user.save()
        user.socio.save()

        return VerifyEmail(ok=True)


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
                      email=email, verified_email=True,
                      data_nascimento=data_nascimento, whatsapp=whatsapp, rg=rg, apelido=apelido)
        socio.save()

        context = {
            'socio': socio,
        }

        socio.notificar(metodo='email', subject='Bem vind@ à plataforma de sócios @aaafuria!',
                        text_template='novo_user.txt', html_template='novo_user.html', context=context)
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
            raise Exception('Sócio não encontrado.')
        except Exception as e:
            raise Exception(e)


class AssociacaoManual(graphene.Mutation):

    class Arguments:
        matricula = graphene.String(required=True)
        tipo_plano = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, matricula, tipo_plano):
        if not info.context.user.is_authenticated:
            raise Exception('Usuário não autenticado.')
        if not info.context.user.is_staff:
            raise Exception('Acesso negado.')

        try:
            valores_tipo_plano = {
                'Mensal': {'valor': 24.9, 'dias': 30},
                'Semestral': {'valor': 99.5, 'dias': 180},
                'Anual': {'valor': 198.0, 'dias': 365},
            }
            socio: Socio = Socio.objects.get(user__username=matricula)

            socio.is_socio = True
            socio.data_inicio = timezone.now()
            socio.data_fim = timezone.now(
            ) + datetime.timedelta(days=valores_tipo_plano[tipo_plano]['dias'])
            socio.save()

            if socio.data_fim.year > timezone.now().year:
                socio.data_fim = timezone.datetime(
                    timezone.now().year, 12, 31, 23, 59, 59
                )

            elif socio.data_fim - timezone.now() > timezone.timedelta(days=31):
                if timezone.now().month < 7:
                    if socio.data_fim.month > 6:
                        socio.data_fim = timezone.datetime(
                            timezone.now().year, 6, 30, 23, 59, 59
                        )

            socio.save()

            conta, _ = Conta.objects.get_or_create(socio=socio)
            if conta.socio.is_socio:
                conta.calangos += int(
                    ((valores_tipo_plano[tipo_plano]['valor'] // 5) * 50))
            conta.save()

            aaafuria = Socio.objects.get(user__username="22238742")
            movimentacao = Movimentacao.objects.create(
                conta_origem=conta,
                conta_destino=aaafuria.conta,
                descricao=f'ASSOCIAÇÃO DE [{socio.apelido}] PARA [{aaafuria.apelido}] | MODE: ASSOCIACAO MANUAL',
                valor=valores_tipo_plano[tipo_plano]['valor'],
                resolvida=True,
                resolvida_em=timezone.now()
            )
            movimentacao.save()

            ok = True
            return AssociacaoManual(ok=ok)
        except Socio.DoesNotExist:
            raise Exception('Sócio não encontrado.')
        except Exception as e:
            raise Exception(e)


class Query(graphene.ObjectType):
    socio = graphene.relay.Node.Field(SocioRelay)
    socio_autenticado = graphene.Field(SocioRelay)
    socio_by_matricula = graphene.Field(
        SocioRelay, matricula=graphene.String(required=False))
    all_socio = DjangoFilterConnectionField(SocioRelay)

    query_stripe_portal_url = graphene.Field(SocioRelay)

    def resolve_socio_autenticado(self, info, **kwargs):
        if info.context.user.is_authenticated:
            return get_object_or_404(Socio, user=info.context.user)

    def resolve_socio_by_matricula(self, info, matricula=None):
        return get_object_or_404(Socio, user__username=matricula)

    def resolve_query_stripe_portal_url(self, info, **kwargs):
        if info.context.user.is_authenticated:
            return get_object_or_404(Socio, user=info.context.user)


class Mutation(graphene.ObjectType):
    novo_user = NovoUser.Field()
    novo_pagamento = NovoPagamento.Field()
    associacao_manual = AssociacaoManual.Field()
    verify_email = VerifyEmail.Field()
