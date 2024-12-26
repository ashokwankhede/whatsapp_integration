from django.urls import path
from messaging import views

urlpatterns = [
    path('', views.send_message, name='send_message'),
    path('whatsapp_webhook', views.whatsapp_webhook, name='whatsapp_webhook'),
    path('get-table-history', views.get_table_history, name="get-table-history")
]