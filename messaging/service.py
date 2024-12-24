import requests
from celery import shared_task
from celery.exceptions import Retry

class WhatsAppService:
    def __init__(self):
        self.url = "https://graph.facebook.com/v21.0/104540952724423/messages"
        self.headers = {
            "Authorization": "Bearer EAAYHZCszimyQBO6DV50rX4fSv9PwXVYCkZCE9eAAuW98Ogmzr7SnyXQDy5YQ5RmWKlDMkC2qwW1NHsJHSpdG0C5yfsjAdzNoILPFtypQpouXWvvkSRdILfmtXdV9YhkwZA1RFnt9Q2AmGADuJuFhDMjCpxJdAiB3jhhzRiVUd2XEUAV4MLLMCVUTLr198ZCzg560tu9YTpYLKYkqagtYH4X2zxQZD",
            "Content-Type": "application/json",
        }

    def process_webhook(self, data):
        """
        Processes incoming webhook data and extracts relevant message information.
        """
        webhook_messages = []
        for e in data:
            changes = e.get('changes', [])
            for change in changes:
                value = change.get('value', {})
                messages = value.get('messages', [])
                for msg in messages:
                    webhook_messages.append({
                        "sender": msg.get('from'),
                        "receiver": value.get('metadata', {}).get('display_phone_number'),
                        "content": msg.get('text', {}).get('body', ''),
                        "status": "RECEIVED"
                    })

        return webhook_messages

    