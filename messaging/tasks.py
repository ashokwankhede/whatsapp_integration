
from .service import WhatsAppService
from celery import shared_task
import logging
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=3 * 60)
def send_message_task(self, mobile_no, message):
    """
    Celery task for sending WhatsApp messages with retry logic.
    
    Parameters:
    - `mobile_nos`: A single mobile number.
    - `message`: The message to be sent.
    
    Retries:
    - Will retry up to `max_retries` times with a delay of `default_retry_delay` seconds.
    - Retries expire after a certain period, using Celery's retry mechanism.
    """
    whatsapp_service = WhatsAppService()
    response = whatsapp_service.send_message(mobile_no=mobile_no, message=message)
    return response

    