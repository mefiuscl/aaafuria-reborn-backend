from django.contrib import admin

import ecommerce.models as ecommerce_models


@admin.register(ecommerce_models.Produto)
class ProdutoAdmin(admin.ModelAdmin):
    pass


@admin.register(ecommerce_models.ProdutoPedido)
class ProdutoPedidoAdmin(admin.ModelAdmin):
    pass


@admin.register(ecommerce_models.Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    pass


@admin.register(ecommerce_models.VariacaoProduto)
class VariacaoProdutoAdmin(admin.ModelAdmin):
    pass
