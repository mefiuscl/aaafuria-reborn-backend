from django.contrib import admin

from members.models import Attachment, Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    search_fields = ('email', 'name', 'registration',)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    pass
