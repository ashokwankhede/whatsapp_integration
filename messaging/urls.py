from django.urls import path
from messaging import views

urlpatterns = [
    path('whatsapp_webhook', views.whatsapp_webhook),
    path('', views.send_message, name='send_message'),
]