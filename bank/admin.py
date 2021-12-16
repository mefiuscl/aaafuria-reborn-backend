from django.contrib import admin

from .models import Conta, Movimentacao


@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    pass


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    pass
