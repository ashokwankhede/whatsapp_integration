import requests
import json
from .models import WhatsAppMessage
import logging
logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        self.url = "https://graph.facebook.com/v21.0/551602171364742/messages"
        self.headers = {
            "Authorization": "Bearer EAAPp0EdFjMYBOwF7aZBocSuScGBEZAjupJYnDsBtoZCJKWgvSszONe2FIG367jrwBExgLQPUVAIOjqZBIRSVXlMJaZB9US3UJ0nkc8PGthuB9OAb7GSBToWX8rwfBjzNG4n4udFJjDH5gfNo4JGYre8tbQiVz3jNugxjYFITmpH3CJG8rW6wZAmpa9y2ZAqGhKp6OiabPUO5Gqs1wgOk1zdXi81jUsZD",
            "Content-Type": "application/json",
        }

    def process_webhook(self, data):
        """
        Processes incoming webhook data and extracts relevant message information.
        """
        webhook_messages = {}
        def get_entry(data):
            if isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, (dict, list)):
                        get_entry(val)
                    else:
                        webhook_messages[key] = val
            elif isinstance(data, list):
                for item in data:
                    get_entry(item)
        
        get_entry(data[0]['changes'])
        
        try:
            message = None
            try:
                message_id = data[0]['changes'][0]['value']['statuses'][0]['id']
                message = WhatsAppMessage.objects.get(message_id=message_id)
            except WhatsAppMessage.DoesNotExist:
                logger.info(f"WhatsApp message with ID {message_id} not found in the database.")
            except KeyError as e:
                logger.info(f"KeyError while retrieving message ID: {e}")
            except Exception as e:
                logger.error(f"Unexpected error while fetching message: {e}", exc_info=True)

            if message:
                if message.status and message.status.lower() != 'read':
                    message.status = webhook_messages.get('status', '').upper()
                    message.save()
            else:
                sender_id = webhook_messages.get('wa_id', '')
                body = webhook_messages.get('body', '')
                status = webhook_messages.get('status', 'RECEIVED').upper()
                
                if sender_id and body:
                    formatted_sender = f"+{sender_id[:2]} {sender_id[2:]}"
                    WhatsAppMessage.objects.create(
                        message_id=webhook_messages.get('id'),
                        sender=sender_id,
                        receiver="+1(555) 1828990",
                        content=webhook_messages.get('body', ''),
                        status=status
                    )
        except Exception as e:
            logger.error(f"Error saving message: {e}", exc_info=True)


        return webhook_messages
    

    def send_message(self, mobile_no, message):
        
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": mobile_no,
                "text": {"body": message},
            }

            response = requests.post(self.url, json=payload, headers=self.headers)

            if response.status_code not in (201, 200):
                logger.info(f"Token expired please refresh it")
                return "Toke Expired"
            
            response = json.loads(response.text)
            logger.info(f"Type of returned response: {type(response)}, {response}")
            logger.info("response sent")
        
            try:
                
                WhatsAppMessage.objects.create(
                    message_id = response['messages'][0]['id'],
                    sender="+1(555) 1828990",
                    receiver=mobile_no,
                    content = message,
                    status = 'SENT'
                )
            except Exception as e:
                logger.info(f"Error saving message: {e}")
                response.raise_for_status()
                logger.info(f"Message sent to {mobile_no}")

                return "Message sending task completed."

        except requests.exceptions.RequestException as exc:
            logger.info("Retry limit reached or expired.")
            return "Failed to send message after retries."


    