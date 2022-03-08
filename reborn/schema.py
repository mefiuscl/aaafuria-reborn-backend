import graphene
import graphql_jwt

import core.schema
import ecommerce.schema
import atividades.schema
import bank.schema
import eventos.schema
import files.schema
import help.schema


class Query(
    core.schema.Query,
    ecommerce.schema.Query,
    atividades.schema.Query,
    bank.schema.Query,
    eventos.schema.Query,
    files.schema.Query,
    help.schema.Query,
    graphene.ObjectType
):
    pass


class Mutation(
    core.schema.Mutation,
    ecommerce.schema.Mutation,
    atividades.schema.Mutation,
    bank.schema.Mutation,
    eventos.schema.Mutation,
    files.schema.Mutation,
    help.schema.Mutation,
    graphene.ObjectType
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
