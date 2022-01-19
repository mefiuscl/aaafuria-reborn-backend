from django.contrib import admin

import ecommerce.models as ecommerce_models


@admin.register(ecommerce_models.Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'preco_socio',
                    'estoque', 'has_variations', 'is_hidden']


@admin.register(ecommerce_models.ProdutoPedido)
class ProdutoPedidoAdmin(admin.ModelAdmin):
    list_display = ['get_socio', 'produto',
                    'variacao', 'quantidade', 'ordered']
    list_filter = ['ordered', 'variacao__nome', 'produto__nome']
    search_fields = ['user__socio__nome', 'user__socio__email',
                     'user__socio__matricula', 'produto__nome', 'variacao__nome']

    def get_socio(self, obj):
        return obj.user.socio

    get_socio.short_description = 'User'


@admin.register(ecommerce_models.Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    list_display = ['get_socio', 'total', 'data_pago', 'ordered']
    list_filter = ['ordered']

    def get_socio(self, obj):
        return obj.user.socio

    get_socio.short_description = 'User'


@admin.register(ecommerce_models.VariacaoProduto)
class VariacaoProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'preco_socio',
                    'estoque']


@admin.register(ecommerce_models.Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    pass
