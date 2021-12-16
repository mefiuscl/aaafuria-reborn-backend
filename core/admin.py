from django.contrib import admin

import core.models as core_models


@admin.register(core_models.Socio)
class SocioAdmin(admin.ModelAdmin):
    pass


@admin.register(core_models.Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    pass


@admin.register(core_models.TipoPlano)
class TipoPlanoAdmin(admin.ModelAdmin):
    pass
