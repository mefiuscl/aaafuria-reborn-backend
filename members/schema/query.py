import graphene
from members.models import Member


class Query(graphene.ObjectType):
    check_member = graphene.Boolean(
        registration=graphene.String(required=True))

    def resolve_check_member(self, info, registration):
        try:
            Member.objects.get(registration=registration)
            return True
        except:
            return False
