from django.contrib import admin

from members.models import Attachment, Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    pass
