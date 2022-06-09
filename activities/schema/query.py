import graphene
from activities.models import Activity, Schedule
from activities.schema.nodes import SchedulePaginatedNode
from django.utils.translation import gettext as _
from graphql import GraphQLError
from utils.utils import get_paginator


class Query(graphene.ObjectType):
    all_activities = graphene.List('activities.schema.nodes.ActivityNode')

    def resolve_all_activities(self, info):
        return Activity.objects.all()
