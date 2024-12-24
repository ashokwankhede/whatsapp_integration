import requests
from celery import shared_task
from celery.exceptions import Retry

class WhatsAppService:
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

    