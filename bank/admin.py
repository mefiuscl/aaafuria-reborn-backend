from django.contrib import admin

from .models import Conta, Movimentacao

admin.site.register(Conta)
admin.site.register(Movimentacao)
