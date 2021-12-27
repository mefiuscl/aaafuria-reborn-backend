from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

import core.models as core_models


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


class CustomUserAdmin(admin.ModelAdmin):
    @admin.action(description='Definir selecionados como Staff')
    def set_staff(self, request, queryset):
        queryset.update(is_staff=True)

    actions = [set_staff]
    form = UserChangeForm
    fieldsets = UserAdmin.fieldsets

    list_display = ('username', 'email', 'is_staff',
                    'is_superuser', 'is_active')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@ admin.register(core_models.Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('apelido', 'is_socio', 'nome',
                    'turma', 'matricula', 'whatsapp_url_link')
    list_filter = ('turma', 'is_socio')
    search_fields = ('apelido', 'nome', 'matricula')

    def whatsapp_url_link(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.whatsapp_url)


@ admin.register(core_models.Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    pass


@ admin.register(core_models.TipoPlano)
class TipoPlanoAdmin(admin.ModelAdmin):
    pass
