import requests
from .models import WhatsAppMessage
import logging
logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        self.url = "https://graph.facebook.com/v21.0/104540952724423/messages"
        self.headers = {
            "Authorization": "Bearer EAAYHZCszimyQBO7XKGOgRPGfW1Y3uX4V9b5Lb1j5bARlSwNZCm0ZADZABZBJOFjVl3VYl51EdJZADyB7ScqpXGfSgoD96Y8S2mSzd0hDlLWku5c2WoKALsPY5fwwzLJtOsbOTKGC078O6jlKUSBi3drswGu1WXY7OypOnfI60Sb5zXJZB0r7wLh2PZCSCq3eFccBaFNaRZC92bxH0tOSNU47J8zPfD40ZD",
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
    

    def send_message(self, mobile_no, message):
        
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": mobile_no,
                "text": {"body": message},
            }

            response = requests.post(self.url, json=payload, headers=self.headers)
            logger.info("response sent")
            try:
                WhatsAppMessage.objects.create(
                    sender="(555) 014-9241",
                    receiver=mobile_no,
                    content=message,
                    status="SENT"
                )
            except Exception as e:
                logger.info(f"Error saving message: {e}")

            response.raise_for_status()
            logger.info(f"Message sent to {mobile_no}")

            return "Message sending task completed."

        except requests.exceptions.RequestException as exc:
            logger.info("Retry limit reached or expired.")
            return "Failed to send message after retries."


    