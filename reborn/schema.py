import atividades.schema
import bank.schema.mutation as bank_mutation
import bank.schema.query as bank_query
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
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphql import GraphQLError


class UserNode(DjangoObjectType):
    member = graphene.Field('members.schema.nodes.MemberNode')

    class Meta:
        model = User
        interfaces = (graphene.relay.Node, )
        filter_fields = []


class Query(
    core.schema.Query,
    ecommerce.schema.Query,
    atividades.schema.Query,
    bank_query.Query,
    eventos.schema.Query,
    files.schema.Query,
    help.schema.Query,
    partnerships.schema.Query,
    members_query.Query,
    memberships_query.Query,
    graphene.ObjectType
):
    user = graphene.Field(UserNode)

    def resolve_user(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError(_('You must be logged in to access this data'))
        return user


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserNode)

    @classmethod
    def resolve(self, root, info, **kwargs):
        return self(user=info.context.user)


class Mutation(
    core.schema.Mutation,
    ecommerce.schema.Mutation,
    atividades.schema.Mutation,
    bank_mutation.Mutation,
    eventos.schema.Mutation,
    files.schema.Mutation,
    help.schema.Mutation,
    members_mutation.Mutation,
    memberships_mutation.Mutation,
    graphene.ObjectType
):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
