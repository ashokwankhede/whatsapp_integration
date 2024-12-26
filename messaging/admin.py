from django.contrib import admin
from .models import WhatsAppMessage, WhatsappContacts

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp', 'status', 'message_id')


@admin.register(WhatsappContacts)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'timestamp')