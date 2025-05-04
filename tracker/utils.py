# tracker/utils.py
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings

logger = logging.getLogger('tracker')

def send_whatsapp_message(to_number, message_body):
    """
    Send a WhatsApp message using Twilio API.
    
    Args:
        to_number (str): The recipient's phone number
        message_body (str): The message content to send
        
    Returns:
        str or None: The message SID if successful, None if failed
        
    Raises:
        No exceptions are raised as they are caught and logged internally
    """
    # Validate inputs
    if not to_number or not message_body:
        logger.error("Invalid parameters: phone number or message body is empty")
        return None
        
    try:
        # Initialize Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Format the phone number for WhatsApp
        whatsapp_number = f'whatsapp:{to_number}'
        
        # Send the message
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            body=message_body,
            to=whatsapp_number
        )
        
        # Log success
        logger.info(f"WhatsApp message sent to {to_number}: {message.sid}")
        return message.sid
        
    except TwilioRestException as e:
        # Log Twilio-specific errors
        logger.error(f"Twilio error sending WhatsApp message to {to_number}: {str(e)}")
        return None
    except Exception as e:
        # Log any other unexpected errors
        logger.error(f"Unexpected error sending WhatsApp message to {to_number}: {str(e)}")
        return None
