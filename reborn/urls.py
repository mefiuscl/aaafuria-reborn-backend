
from django.contrib import admin
from django.urls import path, include
from graphene_django.views import GraphQLView
from django.contrib.auth import views as auth_views

from django.views.decorators.csrf import csrf_exempt


from core.views import core_webhook
from ecommerce.views import ecommerce_webhook
from bank.views import bank_webhook

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path("core_webhook/", csrf_exempt(core_webhook)),
    path("ecommerce_webhook/", csrf_exempt(ecommerce_webhook)),
    path("bank_webhook/", csrf_exempt(bank_webhook)),
    path(
        'admin/password_reset/',
        auth_views.PasswordResetView.as_view(),
        name='admin_password_reset'
        ),
    path(
        'admin/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'
        ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
        ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
        ),
]
