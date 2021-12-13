from django.contrib import admin
from .models import Competidor, Modalidade, Programacao


class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    filter_horizontal = ('competidores',)


class ProgramacaoAdmin(admin.ModelAdmin):
    filter_horizontal = ('competidores_confirmados', 'competidores_presentes')


admin.site.register(Competidor)
admin.site.register(Modalidade, ModalidadeAdmin)
admin.site.register(Programacao, ProgramacaoAdmin)
