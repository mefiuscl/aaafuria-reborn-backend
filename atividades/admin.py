from django.contrib import admin
from .models import Competidor, Modalidade, Programacao


@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    filter_horizontal = ('competidores',)


@admin.register(Programacao)
class ProgramacaoAdmin(admin.ModelAdmin):
    filter_horizontal = ('competidores_confirmados', 'competidores_presentes')


@admin.register(Competidor)
class CompetidorAdmin(admin.ModelAdmin):
    pass
