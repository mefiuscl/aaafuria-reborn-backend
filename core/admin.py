from django.contrib import admin
from django.contrib.auth import UserAdmin
from django.contrib.auth.models import User

import core.models as core_models


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    @admin.action(description='Definir selecionados como Staff')
    def set_staff(self, request, queryset):
        queryset.update(is_staff=True)

    actions = [set_staff]


@admin.register(core_models.Socio)
class SocioAdmin(admin.ModelAdmin):
    pass


@admin.register(core_models.Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    pass


@admin.register(core_models.TipoPlano)
class TipoPlanoAdmin(admin.ModelAdmin):
    pass
