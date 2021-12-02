import graphene
import graphql_jwt

import core.schema
import ecommerce.schema


class Query(core.schema.Query, ecommerce.schema.Query, graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    novo_user = core.schema.NovoUser.Field()
    novo_pagamento = core.schema.NovoPagamento.Field()

    adicionar_ao_carrinho = ecommerce.schema.AdicionarAoCarrinho.Field()
    remover_do_carrinho = ecommerce.schema.RemoverDoCarrinho.Field()

    stripe_checkout = ecommerce.schema.StripeCheckout.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
