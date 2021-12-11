import graphene
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.node.node import from_global_id

from .models import Carrinho, Produto, ProdutoPedido, VariacaoProdutos


class ProdutoType(DjangoObjectType):
    class Meta:
        model = Produto
        filter_fields = []


class ProdutoPedidoType(DjangoObjectType):
    class Meta:
        model = ProdutoPedido
        filter_fields = []


class ProdutoPedidoRelay(DjangoObjectType):
    class Meta:
        model = ProdutoPedido
        filter_fields = ['ordered']
        interfaces = (graphene.relay.Node, )


class ProdutoRelay(DjangoObjectType):
    class Meta:
        model = Produto
        filter_fields = '__all__'
        interfaces = (graphene.relay.Node, )


class CarrinhoType(DjangoObjectType):
    class Meta:
        model = Carrinho
        filter_fields = []


class CarrinhoRelay(DjangoObjectType):
    class Meta:
        model = Carrinho
        filter_fields = ['ordered']
        interfaces = (graphene.relay.Node, )


class VariacaoRelay(DjangoObjectType):
    class Meta:
        model = VariacaoProdutos
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


class StripeCheckoutPlantao(graphene.Mutation):
    class Arguments:
        matricula_socio = graphene.String(required=True)

    ok = graphene.Boolean()
    carrinho = graphene.Field(CarrinhoType)

    def mutate(self, info, matricula_socio):
        carrinho = Carrinho.objects.get(
            user__username=matricula_socio, ordered=False)
        carrinho.create_stripe_checkout_session()
        carrinho.set_short_stripe_link(carrinho.stripe_checkout_url)
        carrinho.save()
        return StripeCheckout(carrinho=carrinho, ok=True)


class RemoverDoCarrinho(graphene.Mutation):
    class Arguments:
        produto_pedido_id = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, produto_pedido_id):
        try:
            if not info.context.user.is_authenticated:
                raise Exception('Usuário não autenticado')

            produto_pedido = ProdutoPedido.objects.get(
                id=from_global_id(produto_pedido_id)[1])
            produto_pedido.delete()
            Carrinho.objects.get(user=info.context.user,
                                 ordered=False).get_total()
            return RemoverDoCarrinho(ok=True)
        except Exception as e:
            print(e)
            return RemoverDoCarrinho(ok=False)


class AdicionarAoCarrinho(graphene.Mutation):
    class Arguments:
        product_id = graphene.String(required=True)
        quantidade = graphene.Int(required=True)
        variacao_id = graphene.String(required=False)

    ok = graphene.Boolean()
    carrinho = graphene.Field(CarrinhoType)

    def mutate(self, info, product_id, quantidade, variacao_id=None):
        try:
            if not info.context.user.is_authenticated:
                raise Exception('Usuário não autenticado.')

            user = info.context.user
            produto = Produto.objects.get(id=from_global_id(product_id)[1])
            variacao = VariacaoProdutos.objects.get(
                id=from_global_id(variacao_id)[1], produto=produto) if variacao_id else None

            carrinho, _ = Carrinho.objects.get_or_create(
                user=user, ordered=False)

            produto_pedido, created = ProdutoPedido.objects.get_or_create(
                produto=produto, user=user, ordered=False, variacao=variacao)

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


class AdicionarAoCarrinhoPlantao(graphene.Mutation):
    class Arguments:
        product_id = graphene.String(required=True)
        quantidade = graphene.Int(required=True)
        matricula_socio = graphene.String(required=True)
        variacao_id = graphene.String(required=False)

    ok = graphene.Boolean()
    carrinho = graphene.Field(CarrinhoType)

    def mutate(self, info, product_id, quantidade, matricula_socio, variacao_id=None,):
        try:
            if not info.context.user.is_authenticated:
                raise Exception('Usuário não autenticado.')

            if not info.context.user.is_staff:
                raise Exception('Usuário não autorizado.')

            user = User.objects.get(username=matricula_socio)
            produto = Produto.objects.get(id=from_global_id(product_id)[1])
            variacao = VariacaoProdutos.objects.get(
                id=from_global_id(variacao_id)[1], produto=produto) if variacao_id else None

            carrinho, _ = Carrinho.objects.get_or_create(
                user=user, ordered=False)

            produto_pedido, created = ProdutoPedido.objects.get_or_create(
                produto=produto, user=user, ordered=False, variacao=variacao)

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

    ok = graphene.Boolean()

    def mutate(self, info, produto_pedido_id, matricula_socio):
        try:
            if not info.context.user.is_authenticated:
                raise Exception('Usuário não autenticado')
            if not info.context.user.is_staff:
                raise Exception('Acesso negado')

            user = User.objects.get(username=matricula_socio)
            produto_pedido = ProdutoPedido.objects.get(
                id=from_global_id(produto_pedido_id)[1])
            produto_pedido.delete()
            Carrinho.objects.get(user=user,
                                 ordered=False).get_total()
            return RemoverDoCarrinho(ok=True)
        except Exception as e:
            print(e)
            return RemoverDoCarrinho(ok=False)


class Query(graphene.ObjectType):
    produto = graphene.relay.Node.Field(ProdutoRelay)
    variacao = graphene.relay.Node.Field(VariacaoRelay)
    variacao_by_product_id = graphene.List(
        VariacaoRelay, id=graphene.String(required=True))

    all_produto = DjangoFilterConnectionField(ProdutoRelay)
    all_variacao = DjangoFilterConnectionField(VariacaoRelay)

    produto_pedido = graphene.Field(ProdutoPedidoType)
    all_produto_pedido = DjangoFilterConnectionField(ProdutoPedidoRelay)

    carrinho = graphene.relay.Node.Field(CarrinhoType)
    all_carrinho = DjangoFilterConnectionField(CarrinhoRelay)

    user_carrinho = graphene.Field(CarrinhoType)
    plantao_carrinho = graphene.Field(
        CarrinhoType, matricula_socio=graphene.String(required=True))

    def resolve_variacao_by_product_id(self, info, id):
        variacao_produto = VariacaoProdutos.objects.filter(
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
