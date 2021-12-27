from django.contrib import admin
from .models import Competidor, Modalidade, Programacao

from core.models import Socio


@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    filter_horizontal = ('competidores',)
    readonly_fields = ('responsavel',)

    def save_model(self, request, obj, form, change):
        obj.responsavel = Socio.objects.filter(user=request.user).first()
        super().save_model(request, obj, form, change)


@admin.register(Programacao)
class ProgramacaoAdmin(admin.ModelAdmin):
    filter_horizontal = ('competidores_confirmados', 'competidores_presentes')
    readonly_fields = ('estado',)


@admin.register(Competidor)
class CompetidorAdmin(admin.ModelAdmin):
    pass
