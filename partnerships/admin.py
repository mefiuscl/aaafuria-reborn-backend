from django.contrib import admin

import partnerships.models as partnerships_models


@admin.register(partnerships_models.Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    pass
