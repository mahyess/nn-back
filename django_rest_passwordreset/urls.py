""" URL Configuration for core auth
"""
from django.urls import path

from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm

app_name = 'password_reset'

urlpatterns = [
    path('confirm/', reset_password_confirm, name="reset-password-confirm"),
    path('', reset_password_request_token, name="reset-password-request"),
]
