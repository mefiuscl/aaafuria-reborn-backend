
from django.contrib import admin
from django.urls import path, include
from graphene_django.views import GraphQLView

from django.views.decorators.csrf import csrf_exempt

from .views import index

from core.views import core_webhook
from ecommerce.views import ecommerce_webhook
from bank.views import bank_webhook
from eventos.views import eventos_webhook

urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path("core_webhook/", csrf_exempt(core_webhook)),
    path("ecommerce_webhook/", csrf_exempt(ecommerce_webhook)),
    path("bank_webhook/", csrf_exempt(bank_webhook)),
    path("eventos_webhook/", csrf_exempt(eventos_webhook)),
]
