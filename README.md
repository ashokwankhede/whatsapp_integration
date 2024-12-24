# Project Setup Guide

Follow the steps below to set up and run the project:

## 1. Clone the Project

```bash
git clone <repository_url>
cd <repository_directory>
```

## 2. Create a Virtual Environment

```bash
python -m venv env
source env/bin/activate  # For Linux/MacOS
env\Scripts\activate    # For Windows
```

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

## 4. Start Django Project

```bash
python manage.py runserver
```

## 5. Start Redis Server

Ensure Redis is installed and running on your system. Use the command:

```bash
redis-server
```

## 6. Start Celery Worker

```bash
celery -A project_name worker --loglevel=info --pool=solo
```

Replace `project_name` with the name of your Django project.

## 7. Start ngrok Server

Download and install ngrok if not already installed. Start ngrok with the following command:

```bash
ngrok http 8000
```

## 8. Get IP and Webhook Path

After starting ngrok, it will display a public URL, such as:

```
https://846f-117-248-111-159.ngrok-free.app
```

Append your webhook endpoint path to this URL (e.g., `/whatsapp_webhook`). For example:

```
https://846f-117-248-111-159.ngrok-free.app/whatsapp_webhook
```

## 9. Validate Webhook with Meta Developer Account

Use the public URL obtained in the previous step to validate the webhook in your Meta Developer account.

## Ready to Go

Once all the above steps are complete, your project should be up and running!

---

Feel free to contribute to this project or raise issues if you encounter any problems.

