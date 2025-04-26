# tracker/utils.py
from twilio.rest import Client
from django.conf import settings

def send_whatsapp_message(to_number, message_body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        from_=settings.TWILIO_WHATSAPP_FROM,
        body=message_body,
        to=f'whatsapp:{to_number}'  # Example: 'whatsapp:+919999999999'
    )
    print("Message sent:", message)  # This prints the full message object
    return message.sid
