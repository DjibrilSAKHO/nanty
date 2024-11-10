from django.urls import path
from .views.webhook import whatsapp

urlpatterns = [
    path('webhook/whatsapp/', whatsapp.whatsapp_webhook, name='whatsapp-webhook'),
]
