import graphene
import graphql_jwt

import core.schema
import ecommerce.schema
import atividades.schema


class Query(core.schema.Query, ecommerce.schema.Query, atividades.schema.Query, graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    novo_user = core.schema.NovoUser.Field()
    novo_pagamento = core.schema.NovoPagamento.Field()

    adicionar_ao_carrinho = ecommerce.schema.AdicionarAoCarrinho.Field()
    remover_do_carrinho = ecommerce.schema.RemoverDoCarrinho.Field()
    adicionar_ao_carrinho_plantao = ecommerce.schema.AdicionarAoCarrinhoPlantao.Field()
    remover_do_carrinho_plantao = ecommerce.schema.RemoverDoCarrinhoPlantao.Field()

    stripe_checkout = ecommerce.schema.StripeCheckout.Field()
    checkout_plantao = ecommerce.schema.CheckoutPlantao.Field()
    stripe_checkout_plantao = ecommerce.schema.StripeCheckoutPlantao.Field()

    confirmar_competidor_na_programacao = atividades.schema.ConfirmarCompetidorNaProgramacao.Field()
    remover_competidor_na_programacao = atividades.schema.RemoverCompetidorNaProgramacao.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
