import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nanty.settings')
import django
django.setup()

from chatbot.services.message_handler import MessageHandler

handler = MessageHandler()
print("Methods:", dir(handler))
print("Has process_whatsapp_message:", hasattr(handler, "process_whatsapp_message"))
