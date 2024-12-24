# Generated by Django 5.1.4 on 2024-12-23 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsAppMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=255)),
                ('receiver', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('SENT', 'Sent'), ('DELIVERED', 'Delivered'), ('FAILED', 'Failed')], max_length=50)),
            ],
        ),
    ]