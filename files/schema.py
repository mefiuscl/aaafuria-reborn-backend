import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.utils.translation import gettext as _
from graphql_relay import from_global_id

from files.models import File


class FileRelay(DjangoObjectType):
    class Meta:
        model = File
        filter_fields = []
        interfaces = (graphene.relay.Node, )

    def resolve_file(self, info, *args, **kwargs):
        return info.context.build_absolute_uri(self.file.url)


class Query(graphene.ObjectType):
    file = graphene.Field(FileRelay, id=graphene.ID())
    all_files = graphene.List(FileRelay)
    unread_files = graphene.List(FileRelay)

    def resolve_file(self, info, id, **kwargs):
        if info.context.user.is_authenticated:
            if id is not None:
                try:
                    file = File.objects.get(pk=from_global_id(id)[1])
                    file.viewers.add(info.context.user.socio)
                    return file
                except File.DoesNotExist:
                    return GraphQLError(_('File not found'))
            else:
                return GraphQLError(_('File not found'))
        else:
            return GraphQLError(_('You must be logged in to access this data'))

    def resolve_all_files(self, info):
        if info.context.user.is_authenticated:
            return File.objects.all()
        else:
            return GraphQLError(_('You must be logged in to access this data'))

    def resolve_unread_files(self, info):
        if info.context.user.is_authenticated:
            return File.objects.exclude(viewers=info.context.user.socio)
        else:
            return GraphQLError(_('You must be logged in to access this data'))


class LikeFile(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    ok = graphene.Boolean()
    file = graphene.Field(FileRelay)

    def mutate(self, info, id):
        if info.context.user.is_authenticated:
            try:
                file = File.objects.get(pk=from_global_id(id)[1])
                file.likes.add(info.context.user.socio)
                ok = True
                return LikeFile(ok=ok, file=file)
            except File.DoesNotExist:
                return GraphQLError(_('File not found'))
        else:
            return GraphQLError(_('You must be logged in to access this data'))


class Mutation(graphene.ObjectType):
    like_file = LikeFile.Field()
