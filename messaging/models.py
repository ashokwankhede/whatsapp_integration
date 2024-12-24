from django.db import models

class WhatsAppMessage(models.Model):
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('SENT', 'Sent'), ('DELIVERED', 'Delivered'), ('FAILED', 'Failed')])


class WhatsappContacts(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    timestamp = models.DateTimeField(auto_now_add=True)
