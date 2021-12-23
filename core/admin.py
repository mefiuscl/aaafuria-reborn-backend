from django.contrib import admin

import core.models as core_models


@admin.register(core_models.Socio)
class SocioAdmin(admin.ModelAdmin):

    @admin.action(description='Definir sócio como Staff')
    def set_staff(self, request, queryset):
        queryset.update(user__is_staff=True)

    actions = [set_staff]


@admin.register(core_models.Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    pass


@admin.register(core_models.TipoPlano)
class TipoPlanoAdmin(admin.ModelAdmin):
    pass
