from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from rest_framework import status
from .models import WhatsAppMessage, WhatsappContacts
from .tasks import send_message_task
from .service import WhatsAppService
import requests
from django.core.exceptions import ValidationError


class WhatsAppMessageModelTest(TestCase):
    def setUp(self):
        self.message = WhatsAppMessage.objects.create(
            sender="sender@example.com",
            receiver="receiver@example.com",
            content="Hello!",
            status="SENT",
        )

    def test_message_creation(self):
        self.assertEqual(WhatsAppMessage.objects.count(), 1)
        self.assertEqual(self.message.sender, "sender@example.com")
        self.assertEqual(self.message.content, "Hello!")
        self.assertEqual(self.message.status, "SENT")


class WhatsappContactsModelTest(TestCase):
    def setUp(self):
        self.contact = WhatsappContacts.objects.create(
            name="John Doe",
            contact="+1234567890",
        )

    def test_contact_creation(self):
        self.assertEqual(WhatsappContacts.objects.count(), 1)
        self.assertEqual(self.contact.name, "John Doe")
        self.assertEqual(self.contact.contact, "+1234567890")


class WhatsAppWebhookViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('whatsapp_webhook')

    def test_webhook_get_valid_token(self):
        response = self.client.get(
            self.webhook_url,
            {"hub.verify_token": "Hfyc5k82hL", "hub.challenge": "12345"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "12345")

    def test_webhook_get_invalid_token(self):
        response = self.client.get(
            self.webhook_url,
            {"hub.verify_token": "InvalidToken", "hub.challenge": "12345"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content.decode(), "Invalid token")

    @patch("messaging.service.WhatsAppService.process_webhook")
    def test_webhook_post(self, mock_process_webhook):
        mock_process_webhook.return_value = [
            {"sender": "123", "receiver": "456", "content": "Hi", "status": "RECEIVED"}
        ]
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {"display_phone_number": "456"},
                                "messages": [{"from": "123", "text": {"body": "Hi"}}],
                            }
                        }
                    ]
                }
            ]
        }
        response = self.client.post(self.webhook_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsAppMessage.objects.count(), 1)


class SendMessageTaskTest(TestCase):
    @patch("messaging.tasks.requests.post")
    def test_send_message_task(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}

        result = send_message_task("receiver@example.com", "Hello, World!")
        self.assertEqual(result, "Message sending task completed.")
        self.assertEqual(WhatsAppMessage.objects.count(), 1)


class SendMessageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.send_message_url = reverse("send_message")
        self.contact = WhatsappContacts.objects.create(name="John Doe", contact="1234567890")

    @patch("messaging.tasks.send_message_task.apply_async")
    def test_send_message_view_post(self, mock_apply_async):
        data = {"receiver": ["1234567890"], "message": "Hello!"}
        response = self.client.post(self.send_message_url, data)
        self.assertEqual(response.status_code, 302)
        mock_apply_async.assert_called_once_with(args=["1234567890", "Hello!"])

    def test_send_message_view_get(self):
        response = self.client.get(self.send_message_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "send_message.html")


class WhatsAppMessageModelEdgeCasesTest(TestCase):
    def test_empty_content(self):
        message = WhatsAppMessage.objects.create(
            sender="sender@example.com",
            receiver="receiver@example.com",
            content="",
            status="SENT"
        )
        self.assertEqual(message.content, "")


class WhatsappContactsModelEdgeCasesTest(TestCase):
    def test_long_name(self):
        contact = WhatsappContacts.objects.create(
            name="a" * 101,  # Exceeding max length
            contact="+1234567890"
        )
        self.assertEqual(len(contact.name), 101)

class WhatsappContactsModelEdgeCasesTest(TestCase):
    def test_empty_contact(self):
        with self.assertRaises(ValidationError):
            # The empty string will trigger validation error
            contact = WhatsappContacts.objects.create(name="John Doe", contact="")
            contact.full_clean()  # This explicitly triggers model validation


class WhatsAppWebhookViewEdgeCasesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('whatsapp_webhook')

    def test_webhook_post_missing_entry(self):
        response = self.client.post(self.webhook_url, {}, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {"status": "error", "message": "Missing entry data."}
        )

    @patch("messaging.service.WhatsAppService.process_webhook", side_effect=Exception("Processing error"))
    def test_webhook_post_service_error(self, mock_service):
        data = {"entry": [{"changes": []}]}
        response = self.client.post(self.webhook_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
            response.content,
            {"status": "error", "message": "Failed to process WhatsApp service."}
        )


class WhatsAppServiceTest(TestCase):
    def setUp(self):
        self.service = WhatsAppService()

    def test_process_webhook_valid_data(self):
        data = [
            {
                "changes": [
                    {
                        "value": {
                            "metadata": {"display_phone_number": "456"},
                            "messages": [{"from": "123", "text": {"body": "Hello"}}]
                        }
                    }
                ]
            }
        ]
        result = self.service.process_webhook(data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["sender"], "123")
        self.assertEqual(result[0]["content"], "Hello")

    def test_process_webhook_empty_data(self):
        result = self.service.process_webhook([])
        self.assertEqual(result, [])


class SendMessageTaskEdgeCasesTest(TestCase):
    @patch("messaging.tasks.requests.post")
    def test_send_message_task_api_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("API Error")
        result = send_message_task("receiver@example.com", "Hello, World!")
        self.assertEqual(result, "Failed to send message after retries.")

    @patch("messaging.tasks.requests.post")
    def test_send_message_task_save_error(self, mock_post):
        mock_post.return_value.status_code = 200
        with patch("messaging.tasks.WhatsAppMessage.objects.create") as mock_create:
            mock_create.side_effect = Exception("Database save error")
            result = send_message_task("receiver@example.com", "Hello, World!")
            self.assertEqual(result, "Message sending task completed.")


class SendMessageViewEdgeCasesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.send_message_url = reverse("send_message")

    def test_send_message_view_post_empty_receiver(self):
        response = self.client.post(self.send_message_url, {"message": "Hello!"})
        self.assertEqual(response.status_code, 400)

    def test_send_message_view_post_empty_message(self):
        response = self.client.post(self.send_message_url, {"receiver": ["1234567890"]})
        self.assertEqual(response.status_code, 400)

    def test_send_message_view_post_multiple_receivers(self):
        data = {"receiver": ["1234567890", "0987654321"], "message": "Hello!"}
        with patch("messaging.tasks.send_message_task.apply_async") as mock_task:
            response = self.client.post(self.send_message_url, data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(mock_task.call_count, 2)


class IntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.contact = WhatsappContacts.objects.create(name="John Doe", contact="1234567890")
        self.webhook_url = reverse('whatsapp_webhook')
        self.send_message_url = reverse("send_message")