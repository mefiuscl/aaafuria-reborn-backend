import graphene
from activities.models import Activity, Attachment, Schedule
from django.utils import timezone
from graphene_django import DjangoObjectType


class ActivityNode(DjangoObjectType):
    ytd_schedules_count = graphene.Int()
    future_schedules_count = graphene.Int()
    expected_cost = graphene.Float()

    class Meta:
        model = Activity
        filter_fields = []
        interfaces = (graphene.relay.Node,)

    def resolve_ytd_schedules_count(self, info):
        return self.schedules.filter(start_date__year=timezone.now().year).count()

    def resolve_future_schedules_count(self, info):
        return self.schedules.filter(start_date__gt=timezone.now()).count()

    def resolve_expected_cost(self, info):
        if info.context.user.is_staff:
            schedules = self.schedules.all()
            cost = 0
            for schedule in schedules:
                cost += schedule.cost
            return cost

    def resolve_schedules(self, info, **kwargs):
        return self.schedules.exclude(start_date__lt=(timezone.now() - timezone.timedelta(hours=24)))


class ScheduleNode(DjangoObjectType):
    status = graphene.String()
    confirmed_count = graphene.Int()
    present_count = graphene.Int()
    current_user_confirmed = graphene.Boolean()
    tags = graphene.List(graphene.String)

    class Meta:
        model = Schedule
        filter_fields = ['is_active']
        interfaces = (graphene.relay.Node, )

    def resolve_status(self, info):
        return self.get_status_display()

    def resolve_confirmed_count(self, info):
        return self.users_confirmed.all().count()

    def resolve_present_count(self, info):
        return self.users_present.all().count()

    def resolve_current_user_confirmed(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return False
        return user in self.users_confirmed.all()

    def resolve_tags(self, info):
        tag = Attachment.objects.filter(schedule=self, title='tags').first()
        if tag:
            return tag.content.split(',')


class SchedulePaginatedNode(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(ScheduleNode)
