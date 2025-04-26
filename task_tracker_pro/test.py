from twilio.rest import Client

TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = config('TWILIO_WHATSAPP_FROM')
TWILIO_WHATSAPP_TO = config('TWILIO_WHATSAPP_TO')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

message = client.messages.create(
    body='Testing WhatsApp alert from Django',
    from_='TWILIO_WHATSAPP_FROM',
    to='TWILIO_WHATSAPP_TO'
)

print(message.sid)
