import graphene
from bank.models import Conta, Movimentacao
from core.models import Socio
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay.node.node import from_global_id

from .models import (Carrinho, Pagamento, Produto, ProdutoPedido,
                     VariacaoProduto)


class ProdutoType(DjangoObjectType):
    class Meta:
        model = Produto
        filter_fields = []

    def resolve_imagem(self, info, *args, **kwargs):
        return info.context.build_absolute_uri(self.imagem.url)


class ProdutoPedidoType(DjangoObjectType):
    class Meta:
        model = ProdutoPedido
        filter_fields = []


class ProdutoPedidoRelay(DjangoObjectType):
    get_price = graphene.Float(source='get_price')

    class Meta:
        model = ProdutoPedido
        filter_fields = ['ordered']
        interfaces = (graphene.relay.Node, )


class ProdutoRelay(DjangoObjectType):
    class Meta:
        model = Produto
        filter_fields = ['is_hidden']
        interfaces = (graphene.relay.Node, )

    def resolve_imagem(self, info, *args, **kwargs):
        return info.context.build_absolute_uri(self.imagem.url)


class CarrinhoType(DjangoObjectType):
    stripe_checkout_url = graphene.String(source='stripe_checkout_url')

    class Meta:
        model = Carrinho
        filter_fields = []


class CarrinhoRelay(DjangoObjectType):
    stripe_checkout_url = graphene.String(source='stripe_checkout_url')

    class Meta:
        model = Carrinho
        filter_fields = ['ordered']
        interfaces = (graphene.relay.Node, )


class VariacaoRelay(DjangoObjectType):
    class Meta:
        model = VariacaoProduto
        filter_fields = ['produto']
        interfaces = (graphene.relay.Node, )


class StripeCheckout(graphene.Mutation):
    ok = graphene.Boolean()
    carrinho = graphene.Field(CarrinhoType)

    def mutate(self, info):
        carrinho = Carrinho.objects.get(user=info.context.user, ordered=False)
        carrinho.create_stripe_checkout_session()
        carrinho.save()
        return StripeCheckout(carrinho=carrinho, ok=True)


class CheckoutPlantao(graphene.Mutation):
    class Arguments:
        checkout_id = graphene.ID(required=True)
        forma_pagamento = graphene.String(required=True)

    ok = graphene.Boolean()
    carrinho = graphene.Field(CarrinhoType)

    def mutate(self, info, checkout_id, forma_pagamento):
        aaafuria = Socio.objects.get(user__username='22238742')
        carrinho = Carrinho.objects.get(id=from_global_id(checkout_id)[1])

        pagamento = Pagamento.objects.create(
            user=carrinho.user,
            carrinho=carrinho,
            forma_pagamento=forma_pagamento,
            status='pago',
            valor=carrinho.total
        )

        movimentacao = Movimentacao.objects.create(
            conta_origem=Conta.objects.get_or_create(
                socio=carrinho.user.socio)[0],
            conta_destino=Conta.objects.get_or_create(
                socio=aaafuria)[0],
            descricao=f'PAGAMENTO PLANTÃO DE [{carrinho.user.socio.apelido}] PARA [{aaafuria.apelido}] | MODE: {forma_pagamento}',
            valor=carrinho.total,
            resolvida=True,
            resolvida_em=timezone.now()
        )
        movimentacao.save()

        carrinho.set_paid()
        carrinho.save()

        pagamento.save()
        return CheckoutPlantao(carrinho=carrinho, ok=True)


class StripeCheckoutPlantao(graphene.Mutation):
    class Arguments:
        checkout_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    carrinho = graphene.Field(CarrinhoType)

    def mutate(self, info, checkout_id):
        carrinho = Carrinho.objects.get(id=from_global_id(checkout_id)[1])
        carrinho.create_stripe_checkout_session()
        carrinho.save()

        carrinho.set_short_stripe_link(carrinho.stripe_checkout_url)
        carrinho.save()
        return StripeCheckoutPlantao(carrinho=carrinho, ok=True)


class AdicionarAoCarrinho(graphene.Mutation):
    class Arguments:
        product_id = graphene.String(required=True)
        quantidade = graphene.Int(required=True)
        variacao_id = graphene.String(required=False)
        observacoes = graphene.String(required=False)

    ok = graphene.Boolean()
    carrinho = graphene.Field(CarrinhoType)

    def mutate(self, info, product_id, quantidade, variacao_id=None, observacoes=None):
        try:
            if not info.context.user.is_authenticated:
                raise GraphQLError(_('Unauthenticated.'))

            user = info.context.user
            produto: Produto = Produto.objects.get(
                id=from_global_id(product_id)[1])

            if produto.exclusivo_competidor and not user.socio.is_atleta:
                raise GraphQLError(_('Produto exclusivo!'))

            variacao = VariacaoProduto.objects.get(
                id=from_global_id(variacao_id)[1], produto=produto) if variacao_id else None

            carrinho, created = Carrinho.objects.get_or_create(
                user=user, ordered=False)

            produto_pedido, created = ProdutoPedido.objects.get_or_create(
                produto=produto, user=user, ordered=False, variacao=variacao, observacoes=observacoes)

            if not created:
                produto_pedido.quantidade += quantidade
                produto_pedido.save()

            produto_pedido.get_price()
            carrinho.produtos.add(produto_pedido)
            carrinho.get_total()
            carrinho.save()
            ok = True
            return AdicionarAoCarrinho(ok=ok, carrinho=carrinho)
        except Produto.DoesNotExist:
            return Exception('Produto não encontrado.')
        except Exception as e:
            return Exception(e)


class RemoverDoCarrinho(graphene.Mutation):
    class Arguments:
        produto_pedido_id = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, produto_pedido_id):
        try:
            if not info.context.user.is_authenticated:
                raise GraphQLError('Unauthenticated.')

            produto_pedido = ProdutoPedido.objects.get(
                id=from_global_id(produto_pedido_id)[1])
            produto_pedido.delete()
            Carrinho.objects.get(user=info.context.user,
                                 ordered=False).get_total()
            return RemoverDoCarrinho(ok=True)
        except Exception as e:
            return Exception(e)


class AdicionarAoCarrinhoPlantao(graphene.Mutation):
    class Arguments:
        product_id = graphene.String(required=True)
        quantidade = graphene.Int(required=True)
        matricula_socio = graphene.String(required=True)
        variacao_id = graphene.String(required=False)
        observacoes = graphene.String(required=False)

    ok = graphene.Boolean()
    carrinho = graphene.Field(CarrinhoType)

    def mutate(self, info, product_id, quantidade, matricula_socio, variacao_id=None, observacoes=None):
        try:
            if not info.context.user.is_authenticated:
                raise Exception('Usuário não autenticado.')

            if not info.context.user.is_staff:
                raise Exception('Usuário não autorizado.')

            user = User.objects.get(username=matricula_socio)
            produto = Produto.objects.get(id=from_global_id(product_id)[1])
            variacao = VariacaoProduto.objects.get(
                id=from_global_id(variacao_id)[1], produto=produto) if variacao_id else None

            carrinho, _ = Carrinho.objects.get_or_create(
                user=user, ordered=False)

            produto_pedido, created = ProdutoPedido.objects.get_or_create(
                produto=produto, user=user, ordered=False, variacao=variacao, observacoes=observacoes)

            if not created:
                produto_pedido.quantidade += quantidade
                produto_pedido.save()

            produto_pedido.get_price()
            carrinho.produtos.add(produto_pedido)
            carrinho.get_total()
            carrinho.save()
            ok = True
            return AdicionarAoCarrinho(ok=ok, carrinho=carrinho)
        except Produto.DoesNotExist:
            return Exception('Produto não encontrado.')
        except Carrinho.DoesNotExist:
            return Exception('Carrinho não encontrado.')


class RemoverDoCarrinhoPlantao(graphene.Mutation):
    class Arguments:
        produto_pedido_id = graphene.String(required=True)
        matricula_socio = graphene.String(required=True)
        remove = graphene.Boolean(required=False)

    ok = graphene.Boolean()

    def mutate(self, info, produto_pedido_id, matricula_socio, remove=False):
        try:
            if not info.context.user.is_authenticated:
                raise Exception('Usuário não autenticado')
            if not info.context.user.is_staff:
                raise Exception('Acesso negado')

            user = User.objects.get(username=matricula_socio)
            produto_pedido = ProdutoPedido.objects.get(
                id=from_global_id(produto_pedido_id)[1])

            if remove:
                produto_pedido.delete()
            else:
                if produto_pedido.quantidade > 1:
                    produto_pedido.quantidade -= 1
                    produto_pedido.save()
                else:
                    produto_pedido.delete()

            Carrinho.objects.get(user=user,
                                 ordered=False).get_total()
            return RemoverDoCarrinho(ok=True)
        except Exception as e:
            return Exception(e)


class Query(graphene.ObjectType):
    produto = graphene.relay.Node.Field(ProdutoRelay)
    variacao = graphene.relay.Node.Field(VariacaoRelay)
    variacao_by_product_id = graphene.List(
        VariacaoRelay, id=graphene.String(required=True))

    all_produto = DjangoFilterConnectionField(ProdutoRelay)
    all_variacao = DjangoFilterConnectionField(VariacaoRelay)

    produto_pedido = graphene.Field(ProdutoPedidoType)
    all_produto_pedido = DjangoFilterConnectionField(ProdutoPedidoRelay)

    carrinho = graphene.relay.Node.Field(CarrinhoRelay)
    all_carrinho = DjangoFilterConnectionField(CarrinhoRelay)

    user_carrinho = graphene.Field(CarrinhoType)
    plantao_carrinho = graphene.Field(
        CarrinhoRelay, matricula_socio=graphene.String(required=True))

    def resolve_carrinho(self, info, id):
        carrinho = get_object_or_404(Carrinho, id=id)
        carrinho.get_total()

        return carrinho

    def resolve_variacao_by_product_id(self, info, id):
        variacao_produto = VariacaoProduto.objects.filter(
            produto=from_global_id(id)[1])
        return variacao_produto

    def resolve_user_carrinho(self, info, **kwargs):
        user = info.context.user
        if user.is_authenticated:
            carrinho, _ = Carrinho.objects.get_or_create(
                user=user, ordered=False)
            return carrinho
        return None

    def resolve_plantao_carrinho(self, info, matricula_socio, **kwargs):
        if info.context.user.is_staff:
            user = User.objects.get(username=matricula_socio)
            carrinho, _ = Carrinho.objects.get_or_create(
                user=user, ordered=False)
            return carrinho
        return None


class Mutation(graphene.ObjectType):
    adicionar_ao_carrinho = AdicionarAoCarrinho.Field()
    remover_do_carrinho = RemoverDoCarrinho.Field()
    adicionar_ao_carrinho_plantao = AdicionarAoCarrinhoPlantao.Field()
    remover_do_carrinho_plantao = RemoverDoCarrinhoPlantao.Field()

    stripe_checkout = StripeCheckout.Field()
    checkout_plantao = CheckoutPlantao.Field()
    stripe_checkout_plantao = StripeCheckoutPlantao.Field()
