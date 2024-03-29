from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

import eventos.models as eventos_models


def linkify(field_name):
    """
    Converts a foreign key value into clickable links.

    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id:change
    """
    def _linkify(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return '-'
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f'admin:{app_label}_{model_name}_change'
        link_url = reverse(view_name, args=[linked_obj.pk])
        return format_html('<a href="{}">{}</a>', link_url, linked_obj)

    _linkify.short_description = field_name  # Sets column name
    return _linkify


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
    list_display = ['evento', 'nome', 'quantidade_restante', 'preco',
                    'preco_socio', 'preco_convidado', 'data_inicio', 'data_fim', 'ativo']


@admin.register(eventos_models.Ingresso)
class IngressoAdmin(admin.ModelAdmin):
    readonly_fields = ('get_stripe_checkout_url', )
    list_display = ('evento', 'lote', linkify('participante'),
                    'turma', 'categoria', 'status', )
    list_filter = ('status', 'lote', 'lote__evento', 'participante__categoria')
    search_fields = ['participante__nome',
                     'participante__email', 'lote__evento__nome', 'participante__socio__matricula']

    def evento(self, obj):
        return obj.lote.evento

    def categoria(self, obj):
        return obj.participante.categoria

    def turma(self, obj):
        return obj.participante.socio.turma or None

    def categoria(self, obj):
        return obj.participante.get_categoria_display()


@admin.register(eventos_models.IngressoTransfer)
class IngressoTransferAdmin(admin.ModelAdmin):
    pass
