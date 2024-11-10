from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
import logging
import json
from ...services.message_handler import MessageHandler
from ...utils.constants import WHATSAPP_VERIFY_TOKEN

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_webhook(request):
    """
    Point d'entrée synchrone du webhook WhatsApp.
    """
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        logger.info(f"WhatsApp webhook verification - Mode: {mode}, Token: {token}")

        if mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
            logger.info("Webhook verification successful")
            return HttpResponse(challenge)
        else:
            logger.warning("Webhook verification failed")
            return HttpResponse('Forbidden', status=403)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            with transaction.atomic():
                handler = MessageHandler()
                success = handler.process_whatsapp_message(data)
                
                if success:
                    logger.info("Message traité avec succès")
                    return JsonResponse({'status': 'success'})
                else:
                    logger.error("Échec du traitement du message")
                    return JsonResponse({'status': 'error', 'message': 'Processing failed'}, status=500)

        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Erreur inattendue lors du traitement: {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
