# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import ContactForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
@shared_task
def delete_expired_objects():
    # Define the time threshold for object deletion (e.g., 24 hours ago)
    threshold = timezone.now() - timezone.timedelta(hours=24)

    # Delete objects older than the threshold
    ContactForm.objects.filter(created_at__lt=threshold).delete()

@shared_task
def send_contact_email(name, email, message):
    subject = 'New Contact Form Submission'
    message_body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
    from_email = 'y4165514@gmail.com'  # Use your own email address as the sender

    send_mail(subject, message_body, from_email, ['y4165514@gmail.com'])  # Replace with your email address