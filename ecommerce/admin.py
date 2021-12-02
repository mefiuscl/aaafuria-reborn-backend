from django.contrib import admin

from .models import *

admin.site.register(Produto)
admin.site.register(ProdutoPedido)
admin.site.register(Carrinho)
admin.site.register(VariacaoProdutos)
