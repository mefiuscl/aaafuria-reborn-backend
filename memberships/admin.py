from django.contrib import admin

from memberships.models import Attachment, Membership, MembershipPlan


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    pass


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    pass


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    pass
