import graphene
from activities.models import Activity, Schedule
from activities.schema.nodes import SchedulePaginatedNode
from django.utils.translation import gettext as _
from graphql import GraphQLError
from utils.utils import get_paginator


class Query(graphene.ObjectType):
    all_activities = graphene.List('activities.schema.nodes.ActivityNode')
    all_schedules = graphene.Field(
        'activities.schema.nodes.SchedulePaginatedNode', page=graphene.Int(), page_size=graphene.Int(), status=graphene.String())

    def resolve_all_activities(self, info):
        return Activity.objects.all()

    def resolve_all_schedules(self, info, page=1, page_size=10, **kwargs):
        if info.context.user.is_anonymous:
            raise GraphQLError(_('Unauthenticated.'))

        qs = Schedule.objects.all()

        return get_paginator(qs, page_size, page, SchedulePaginatedNode)
