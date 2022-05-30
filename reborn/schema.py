import atividades.schema
import bank.schema
import core.schema
import ecommerce.schema
import eventos.schema
import files.schema
import graphene
import graphql_jwt
import help.schema
import members.schema.mutation as members_mutation
import members.schema.query as members_query
import memberships.schema.mutation as memberships_mutation
import memberships.schema.query as memberships_query
import partnerships.schema


class Query(
    core.schema.Query,
    ecommerce.schema.Query,
    atividades.schema.Query,
    bank.schema.Query,
    eventos.schema.Query,
    files.schema.Query,
    help.schema.Query,
    partnerships.schema.Query,
    members_query.Query,
    memberships_query.Query,
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
    members_mutation.Mutation,
    memberships_mutation.Mutation,
    graphene.ObjectType
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
