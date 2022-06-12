import graphene
from activities.models import Activity, Attachment, Schedule
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from graphql import GraphQLError
from graphql_relay import from_global_id


class ConfirmToSchedule(graphene.Mutation):
    class Arguments:
        schedule_id = graphene.ID(required=True)
        user_username = graphene.String()

    ok = graphene.Boolean()

    def mutate(self, info, schedule_id, **kwargs):
        user = info.context.user
        user_username = kwargs.get('user_username')

        if not user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))

        if user.is_staff and user_username:
            user = User.objects.get(username=user_username)

        if user.member.has_active_membership is False and user.is_staff is False:
            return ConfirmToSchedule(ok=False)

        schedule = Schedule.objects.get(id=from_global_id(schedule_id)[1])
        schedule.users_confirmed.add(user)
        schedule.refresh()
        schedule.save()

        return ConfirmToSchedule(ok=True)


class CancelFromSchedule(graphene.Mutation):
    class Arguments:
        schedule_id = graphene.ID(required=True)
        user_username = graphene.String()

    ok = graphene.Boolean()

    def mutate(self, info, schedule_id, **kwargs):
        user = info.context.user
        user_username = kwargs.get('user_username')

        if not user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))

        if user.is_staff and user_username:
            user = User.objects.get(username=user_username)

        schedule = Schedule.objects.get(id=from_global_id(schedule_id)[1])
        schedule.users_confirmed.remove(user)
        schedule.refresh()
        schedule.save()

        return CancelFromSchedule(ok=True)


class CreateSchedule(graphene.Mutation):
    class Arguments:
        activity_id = graphene.ID(required=True)
        description = graphene.String(required=True)
        start_date = graphene.DateTime(required=True)
        end_date = graphene.DateTime()
        location = graphene.String(required=True)
        cost = graphene.Float()
        max_participants = graphene.Int(required=True)
        min_participants = graphene.Int(required=True)
        tags = graphene.String()

    ok = graphene.Boolean()
    schedule = graphene.Field('activities.schema.nodes.ScheduleNode')

    def mutate(self, info, activity_id, description, start_date, location, max_participants, min_participants, **kwargs):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))

        if user.is_staff is False:
            raise GraphQLError(_('Unauthorized.'))

        activity = Activity.objects.get(id=from_global_id(activity_id)[1])
        schedule, created = Schedule.objects.get_or_create(
            activity=activity,
            description=description,
            start_date=start_date,
            end_date=kwargs.get('end_date'),
            location=location,
            cost=kwargs.get('cost'),
            max_participants=max_participants,
            min_participants=min_participants
        )

        if not created:
            return CreateSchedule(ok=False, schedule=None)

        if kwargs.get('tags'):
            attachment, c = Attachment.objects.get_or_create(
                schedule=schedule,
                title='tags')
            attachment.content = kwargs.get('tags')
            attachment.save()

        return CreateSchedule(ok=True, schedule=schedule)


class UpdateSchedule(graphene.Mutation):
    class Arguments:
        schedule_id = graphene.ID(required=True)
        description = graphene.String()
        start_date = graphene.DateTime()
        end_date = graphene.DateTime()
        location = graphene.String()
        cost = graphene.Float()
        max_participants = graphene.Int()
        min_participants = graphene.Int()

    ok = graphene.Boolean()
    schedule = graphene.Field('activities.schema.nodes.ScheduleNode')

    def mutate(self, info, schedule_id, description, start_date, location, max_participants, min_participants, **kwargs):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))

        if user.is_staff is False:
            raise GraphQLError(_('Unauthorized.'))

        schedule = Schedule.objects.get(id=from_global_id(schedule_id)[1])
        schedule.description = description
        schedule.start_date = start_date
        schedule.end_date = kwargs.get('end_date')
        schedule.location = location
        schedule.cost = kwargs.get('cost')
        schedule.max_participants = max_participants
        schedule.min_participants = min_participants

        schedule.save()

        return UpdateSchedule(ok=True, schedule=schedule)


class DeleteSchedule(graphene.Mutation):
    class Arguments:
        schedule_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, schedule_id):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))
        if user.is_staff is False:
            raise GraphQLError(_('Unauthorized.'))

        schedule = Schedule.objects.get(id=from_global_id(schedule_id)[1])
        schedule.delete()

        return DeleteSchedule(ok=True)


class EndSchedule(graphene.Mutation):
    class Arguments:
        schedule_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, schedule_id):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))
        if user.is_staff is False:
            raise GraphQLError(_('Unauthorized.'))

        schedule = Schedule.objects.get(id=from_global_id(schedule_id)[1])
        schedule.status = Schedule.ENDED
        schedule.is_active = False
        schedule.save()

        return EndSchedule(ok=True)


class ToggleUserPresence(graphene.Mutation):
    class Arguments:
        schedule_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    presence = graphene.Boolean()

    def mutate(self, info, schedule_id, user_id, **kwargs):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError(_('Unauthenticated.'))
        if user.is_staff is False:
            raise GraphQLError(_('Unauthorized.'))

        schedule = Schedule.objects.get(id=from_global_id(schedule_id)[1])
        user = User.objects.get(id=from_global_id(user_id)[1])

        if user in schedule.users_present.all():
            schedule.users_present.remove(user)
            presence = False
        else:
            schedule.users_present.add(user)
            presence = True

        schedule.refresh()
        schedule.save()

        return ToggleUserPresence(ok=True, presence=presence)


class Mutation(graphene.ObjectType):
    confirm_to_schedule = ConfirmToSchedule.Field()
    cancel_from_schedule = CancelFromSchedule.Field()
    create_schedule = CreateSchedule.Field()
    update_schedule = UpdateSchedule.Field()
    delete_schedule = DeleteSchedule.Field()
    end_schedule = EndSchedule.Field()
    toggle_user_presence = ToggleUserPresence.Field()
