from django.contrib import admin

from .models import Issue, Comment


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
