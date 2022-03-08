import graphene
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import from_global_id

from .models import Issue, Comment


class IssueRelay(DjangoObjectType):
    class Meta:
        model = Issue
        filter_fields = ['status']
        interfaces = (graphene.relay.Node, )


class CommentRelay(DjangoObjectType):
    class Meta:
        model = Comment
        filter_fields = []
        interfaces = (graphene.relay.Node, )


class CreateIssue(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        category = graphene.String(required=True)
        priority = graphene.String(required=True)

    ok = graphene.Boolean()
    issue = graphene.Field(IssueRelay)

    def mutate(self, info, title, description, category, priority):
        if info.context.user.is_authenticated:
            issue = Issue.objects.create(
                author=info.context.user.socio,
                title=title,
                description=description,
                category=category,
                priority=priority,
            )
            return CreateIssue(ok=True, issue=issue)
        else:
            raise GraphQLError(_('You must be logged in to access this data'))


class CloseIssue(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    issue = graphene.Field(IssueRelay)

    def mutate(self, info, id):
        if info.context.user.is_authenticated:
            issue = get_object_or_404(Issue, pk=from_global_id(id)[1])
            if issue.status == Issue.STATUS_CLOSED:
                raise GraphQLError(_('Issue already closed'))
            issue.status = Issue.STATUS_CLOSED
            issue.save()
            return CloseIssue(ok=True, issue=issue)
        else:
            raise GraphQLError(_('You must be logged in to access this data'))


class CreateComment(graphene.Mutation):
    class Arguments:
        issue_id = graphene.ID(required=True)
        description = graphene.String(required=True)

    ok = graphene.Boolean()
    comments = graphene.List(CommentRelay)

    def mutate(self, info, issue_id, description):
        if info.context.user.is_authenticated:
            issue_id = from_global_id(issue_id)[1]
            issue = get_object_or_404(Issue, pk=issue_id)

            if issue.status == Issue.STATUS_CLOSED:
                raise GraphQLError(_('This issue is closed'))

            issue.comments.create(
                author=info.context.user.socio,
                description=description,
            )
            issue.check_status()
            issue.save()
            return CreateComment(ok=True, comments=issue.comments.all())
        else:
            raise GraphQLError(_('You must be logged in to access this data'))


class Query(graphene.ObjectType):
    issue = graphene.Field(IssueRelay, id=graphene.ID())
    issue_comments = graphene.List(CommentRelay, issue_id=graphene.ID())
    socio_issues = DjangoFilterConnectionField(IssueRelay)
    all_issues = DjangoFilterConnectionField(IssueRelay)

    def resolve_issue(self, info, id, **kwargs):
        if info.context.user.is_authenticated:
            if id is not None:
                try:
                    return Issue.objects.get(pk=from_global_id(id)[1])
                except Issue.DoesNotExist:
                    raise GraphQLError(_('Issue not found'))
            else:
                raise GraphQLError(_('Issue not found'))
        else:
            raise GraphQLError(_('You must be logged in to access this data'))

    def resolve_issue_comments(self, info, issue_id, **kwargs):
        if info.context.user.is_authenticated:
            if issue_id is not None:
                try:
                    return Issue.objects.get(pk=from_global_id(issue_id)[1]).comments.all()
                except Issue.DoesNotExist:
                    raise GraphQLError(_('Issue not found'))
            else:
                raise GraphQLError(_('Issue not found'))
        else:
            raise GraphQLError(_('You must be logged in to access this data'))

    def resolve_all_issues(self, info, **kwargs):
        if info.context.user.is_authenticated:
            if not info.context.user.is_staff:
                raise GraphQLError(
                    _('You do not have permission to access this data'))

            return Issue.objects.all()
        else:
            raise GraphQLError(_('You must be logged in to access this data'))

    def resolve_socio_issues(self, info, **kwargs):
        if info.context.user.is_authenticated:
            if not info.context.user.is_staff:
                raise GraphQLError(
                    _('You do not have permission to access this data'))

            return Issue.objects.filter(author=info.context.user.socio)
        else:
            raise GraphQLError(_('You must be logged in to access this data'))


class Mutation(graphene.ObjectType):
    create_issue = CreateIssue.Field()
    create_comment = CreateComment.Field()
    close_issue = CloseIssue.Field()
