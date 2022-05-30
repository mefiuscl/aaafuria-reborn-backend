import graphene
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from members.models import Member


class CreateAccount(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        name = graphene.String(required=True)
        nickname = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=True)
        rg = graphene.String(required=True)
        cpf = graphene.String(required=True)
        birth_date = graphene.String(required=True)
        group = graphene.String(required=True)
        avatar = Upload(required=True)

    ok = graphene.Boolean()
    member = graphene.Field('members.schema.nodes.MemberNode')

    def mutate(self, info, username, password, name, nickname, email, phone, rg, cpf, birth_date, group, avatar):
        if not (username or password or name or nickname or email or phone or rg or cpf or birth_date or group or avatar):
            raise GraphQLError(_('All fields are required'))

        if len(username) != 8:
            raise GraphQLError(_('Username must be 8 characters'))
        if len(password) != 6:
            raise GraphQLError(_('Password must be 6 characters'))
        if not username.isdigit():
            raise GraphQLError(_('Username must be numeric'))
        if not password.isdigit():
            raise GraphQLError(_('Password must be numeric'))

        member = Member.objects.create(
            registration=username,
            name=name,
            nickname=nickname,
            email=email,
            phone=phone,
            rg=rg,
            cpf=cpf,
            birth_date=birth_date,
            group=group,
            avatar=avatar,
            user=User.objects.create_user(
                username=username, password=password, email=email),
        )

        return CreateAccount(ok=True, member=member)


class Mutation(graphene.ObjectType):
    create_account = CreateAccount.Field()
