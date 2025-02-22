import os
import random
import string
from azure.communication.email import EmailClient
from django.conf import settings

AZURE_CONNECTION_STRING = settings.AZURE_EMAIL_CONNECTION_STRING
AZURE_SENDER_EMAIL = settings.AZURE_SENDER_EMAIL

def generate_verification_code(length=6):
    return "".join(random.choices(string.digits, k=length))

def send_verification_email(to_email: str, verification_code: str):
    """Sends an email with a verification code."""
    try:
        client = EmailClient.from_connection_string(AZURE_CONNECTION_STRING)

        message = {
            "senderAddress": AZURE_SENDER_EMAIL,
            "recipients": {"to": [{"address": to_email}]},
            "content": {
                "subject": "Verify Your Email",
                "plainText": f"Your verification code is: {verification_code}",
                "html": f"<p>Your verification code is: <strong>{verification_code}</strong></p>"
            }
        }

        poller = client.begin_send(message)
        result = poller.result()
        return result.get("status") in ["Succeeded", "InProgress"]

    except Exception as ex:
        print(f"Error sending verification email: {ex}")
        return False

def send_password_reset_email(to_email: str, reset_token: str):
    """Sends an email with a password reset link."""
    try:
        client = EmailClient.from_connection_string(AZURE_CONNECTION_STRING)
        
        reset_link = f"https://verified-elf-locally.ngrok-free.app/reset-password?token={reset_token}"
        
        message = {
            "senderAddress": AZURE_SENDER_EMAIL,
            "recipients": {"to": [{"address": to_email}]},
            "content": {
                "subject": "Password Reset Request",
                "plainText": f"Click the link to reset your password: {reset_link}",
                "html": f"<p>Click <a href='{reset_link}'>here</a> to reset your password.</p>"
            }
        }

        poller = client.begin_send(message)
        result = poller.result()
        return result.get("status") in ["Succeeded", "InProgress"]

    except Exception as ex:
        print(f"Error sending password reset email: {ex}")
        return False