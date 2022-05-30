
from bank.views import bank_webhook
from core.views import core_webhook
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from ecommerce.views import ecommerce_webhook
from eventos.views import eventos_webhook
from graphene_file_upload.django import FileUploadGraphQLView

from .views import index

urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("graphql", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),
    path("core_webhook/", csrf_exempt(core_webhook)),
    path("ecommerce_webhook/", csrf_exempt(ecommerce_webhook)),
    path("bank_webhook/", csrf_exempt(bank_webhook)),
    path("eventos_webhook/", csrf_exempt(eventos_webhook)),
]
