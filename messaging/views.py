from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import WhatsAppMessage, WhatsappContacts
from django.http import HttpResponse
from rest_framework import status
from django.shortcuts import render, redirect
from .service import WhatsAppService
from messaging.tasks import send_message_task
import logging
logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
def whatsapp_webhook(request):
    if request.method == 'GET':
        try:
                verify_token = request.GET.get('hub.verify_token')
                challenge = request.GET.get('hub.challenge')

                if verify_token == "Hfyc5k82hL":
                    return HttpResponse(challenge)
                else:
                    logger.warning("Invalid token received.")
                    return HttpResponse("Invalid token", status=403)

        except Exception as e:
            logger.critical(f"Unhandled exception in whatsapp_validate_token: {str(e)}")
            return HttpResponse("An unexpected error occurred.", status=500)
        
    if request.method == 'POST':
        try:
            logger.info(f"Incoming webhook payload: {request.data}")
            data = request.data
            entry = data.get('entry', [])

            if not entry:
                logger.warning("No entry data received in the request.")
                return Response({"status": "error", "message": "Missing entry data."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                whatsapp_service = WhatsAppService()
                response = whatsapp_service.process_webhook(entry)
            except Exception as e:
                logger.error(f"Error processing WhatsApp service: {str(e)}")
                return Response({"status": "error", "message": "Failed to process WhatsApp service."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            for res in response:
                try:
                    WhatsAppMessage.objects.create(
                        sender=res["sender"],
                        receiver=res["receiver"],
                        content=res["content"],
                        status=res["status"]
                    )
                except Exception as e:
                    logger.error(f"Error saving message to database: {str(e)}")
                    return Response({"status": "error", "message": "Failed to save message to database."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.critical(f"Unhandled exception: {str(e)}")
            return Response({"status": "error", "message": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




def send_message(request):
    if request.method == "POST":
        receiver_list = request.POST.getlist("receiver")
        message = request.POST.get("message")

        if not receiver_list or not message:
            return HttpResponse("Receiver and message are required.", status=400)
        for receiver in receiver_list:
            if receiver:
                send_message_task.apply_async(args=[receiver, message])        
        
        return redirect('send_message')

    messages = WhatsAppMessage.objects.all().order_by('-timestamp')
    contacts = WhatsappContacts.objects.all().order_by('-timestamp')
    return render(request, 'send_message.html', {"messages": messages, "contacts": contacts})