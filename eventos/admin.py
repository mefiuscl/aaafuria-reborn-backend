from django.contrib import admin
import eventos.models as eventos_models


@admin.register(eventos_models.Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    pass


@admin.register(eventos_models.Convidado)
class ConvidadoAdmin(admin.ModelAdmin):
    pass


@admin.register(eventos_models.Evento)
class EventoAdmin(admin.ModelAdmin):
    pass


@admin.register(eventos_models.Lote)
class LoteAdmin(admin.ModelAdmin):
    pass


@admin.register(eventos_models.Ingresso)
class IngressoAdmin(admin.ModelAdmin):
    readonly_fields = ('stripe_checkout_url', )
