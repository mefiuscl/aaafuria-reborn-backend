import graphene
from store.models import Item
from store.schema.nodes import ItemPaginatedNode
from utils.utils import get_paginator


class Query(graphene.ObjectType):
    digital_items = graphene.Field(
        'store.schema.nodes.ItemPaginatedNode', page=graphene.Int())
    analog_items = graphene.Field(
        'store.schema.nodes.ItemPaginatedNode', page=graphene.Int())

    def resolve_analog_items(self, info, page):
        page_size = 10
        qs = Item.objects.filter(
            is_analog=True, is_active=True)

        return get_paginator(qs, page_size, page, ItemPaginatedNode)

    def resolve_digital_items(self, info, page):
        page_size = 10
        qs = Item.objects.filter(
            is_digital=True, is_active=True)

        return get_paginator(qs, page_size, page, ItemPaginatedNode)
