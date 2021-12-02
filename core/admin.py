from django.contrib import admin

import core.models as core_models

admin.site.register(core_models.Socio)
admin.site.register(core_models.Pagamento)
admin.site.register(core_models.TipoPlano)
