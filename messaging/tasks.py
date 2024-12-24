
import requests
from celery import shared_task
from .models import WhatsAppMessage


url = "https://graph.facebook.com/v21.0/104540952724423/messages"
headers = {
    "Authorization": "Bearer EAAYHZCszimyQBO4S7fYf0ZCJ0xNvY4N59ZAbW6t3K3EcKdk5Ye5LsMYEZBqWxLLjeSUI0WeIjAWIdGoreshBBGjVSoMENAkWXPm2FpsA6dvEsUM3KGtmRRnqgL1DUUyZAU9qx6N4vIaRo3PQq7g1IQESepjEB2Txcvd8i6se7yR8osClAMSa3vvhEvBhlU9lusCMZD",
    "Content-Type": "application/json",
}
@shared_task(bind=True, max_retries=3, default_retry_delay=10 * 60)
def send_message_task(self, mobile_no, message):
    """
    Celery task for sending WhatsApp messages with retry logic.
    
    Parameters:
    - `mobile_nos`: A single mobile number or a list of numbers.
    - `message`: The message to be sent.
    
    Retries:
    - Will retry up to `max_retries` times with a delay of `default_retry_delay` seconds.
    - Retries expire after a certain period, using Celery's retry mechanism.
    """
    try:
        
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile_no,
            "text": {"body": message},
        }

        response = requests.post(url, json=payload, headers=headers)
        print("response sent")
        try:
            print("Saving Into db")
            print("*"*100)
            WhatsAppMessage.objects.create(
                sender="+1(555) 014-9241",
                receiver=mobile_no,
                content=message,
                status="SENT"
            )
        except Exception as e:
            print(f"Error saving message: {e}")

        response.raise_for_status()
        print(f"Message sent to {mobile_no}")

        return "Message sending task completed."

    except requests.exceptions.RequestException as exc:
        print("Retry limit reached or expired.")
        return "Failed to send message after retries."
