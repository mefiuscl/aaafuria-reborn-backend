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
    list_display = ('evento', 'lote', 'participante', 'status', )
    list_filter = ('status', 'lote__evento')
    search_fields = ['participante__nome',
                     'participante__email', 'lote__evento__nome']

    def evento(self, obj):
        return obj.lote.evento
