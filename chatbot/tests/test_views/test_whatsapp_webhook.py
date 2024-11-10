import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nanty.settings')
import django
django.setup()

from chatbot.views.webhook.whatsapp import whatsapp_webhook
from chatbot.services.message_handler import MessageHandler

# Simulons une requête POST avec un payload complet
class FakeRequest:
    method = 'POST'
    body = b'''
    {
        "entry": [{
            "changes": [{
                "value": {
                    "metadata": {
                        "display_phone_number": "221778431313"
                    },
                    "contacts": [{
                        "profile": {
                            "name": "Test User"
                        }
                    }],
                    "messages": [{
                        "id": "test_message_id",
                        "from": "221773336199",
                        "type": "text",
                        "timestamp": "1699360000",
                        "text": {
                            "body": "Test message"
                        }
                    }]
                }
            }]
        }]
    }
    '''

print("=== Test direct du webhook ===")
handler = MessageHandler()
print("Handler methods:", dir(handler))
request = FakeRequest()
response = whatsapp_webhook(request)
print("Response:", response)
