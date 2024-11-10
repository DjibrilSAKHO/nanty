from dataclasses import dataclass
from typing import Dict, Any, Optional
from django.db import models, transaction
import logging
from django.db.models import Q

from chatbot.models import (
   User, Channel, Platform, ChannelPlatform,
   Conversation, ConversationStep, ConversationStepText, MessageStatus
)

@dataclass
class MessageData:
   message_id: str
   type: str
   from_number: str
   timestamp: str
   display_phone_number: str
   platform_id: int
   contact_name: str
   content: Dict[str, Any]
   message_source: str

@dataclass
class ConversationData:
   conversation: models.Model
   current_step: Optional[models.Model]
   is_new: bool

class MessageHandler:
   def __init__(self):
       print("=== NOUVELLE VERSION DU MESSAGE HANDLER CHARGÉE ===")
       self.logger = logging.getLogger(__name__)

   def process_whatsapp_message(self, payload: Dict[str, Any]) -> bool:
    """
    Point d'entrée historique pour la compatibilité avec le webhook existant.
    Délègue le traitement à handle_message.
    """
    return self.handle_message(payload)

   def handle_message(self, payload: Dict[str, Any]) -> bool:
       """Point d'entrée principal pour le traitement des messages"""
       # Log du payload reçu
       self.logger.info("=== Nouveau message WhatsApp reçu ===")
       self.logger.info(f"Payload: {payload}")

       try:
           with transaction.atomic():
               # 1. Extraire et valider les infos du message
               message_info = self._extract_message_info(payload)
               if not message_info:
                   return False

               # 2. Vérifier et valider le canal
               channel = self._verify_channel(message_info)
               if not channel:
                   return False

               # 3. Récupérer ou créer l'utilisateur
               user = self._get_or_create_user(message_info)
               if not user:
                   return False

               # 4. Gérer la conversation
               conversation_data = self._handle_conversation(user, channel, message_info)
               if not conversation_data:
                   return False

               # 5. Sauvegarder le message et ses données associées
               result = self._save_message(conversation_data, message_info)

               if result:
                   self.logger.info("Message traité avec succès")
               return result

       except Exception as e:
           self.logger.error(f"Erreur lors du traitement du message: {str(e)}")
           return False

   def _extract_message_info(self, payload: Dict[str, Any]) -> Optional[MessageData]:
       """Extrait et valide les informations du message"""
       try:
           entry = payload.get('entry', [{}])[0]
           changes = entry.get('changes', [{}])[0]
           value = changes.get('value', {})
           message = value.get('messages', [{}])[0]

           # Extraire les données de base
           from_number = message.get('from')
           display_number = value['metadata']['display_phone_number']

           # Déterminer message_source
           message_source = 'operator' if from_number == display_number else 'client'

           # Log pour debug
           self.logger.info(f"Numéros comparés - From: {from_number}, Display: {display_number}")
           self.logger.info(f"Message source déterminé: {message_source}")

           message_data = MessageData(
               message_id=message.get('id'),
               type=message.get('type', 'text'),
               from_number=from_number,
               timestamp=message.get('timestamp'),
               display_phone_number=display_number,
               platform_id=1,  # WhatsApp platform ID
               contact_name=value.get('contacts', [{}])[0].get('profile', {}).get('name', ''),
               content=message.get('text', {'body': ''}) if message.get('type') == 'text' else {},
               message_source=message_source
           )

           self.logger.info(f"Informations extraites: {message_data}")
           return message_data

       except Exception as e:
           self.logger.error(f"Erreur lors de l'extraction des informations: {str(e)}")
           return None

   def _verify_channel(self, message_info: MessageData) -> Optional[Channel]:
       """Vérifie l'existence et le statut du canal"""
       try:
           channel = Channel.objects.filter(
               display_phone_number=message_info.display_phone_number,
               status='Enabled'
           ).first()

           if not channel:
               self.logger.error("Canal non trouvé ou désactivé")
               return None

           return channel

       except Exception as e:
           self.logger.error(f"Erreur lors de la vérification du canal: {str(e)}")
           return None

   def _get_or_create_user(self, message_info: MessageData) -> Optional[User]:
       """Récupère ou crée l'utilisateur"""
       try:
           user = User.objects.filter(
               display_phone_number=message_info.from_number
           ).first()

           if not user:
               # Créer un nouvel utilisateur
               user = User.objects.create(
                   category='client',
                   firstname=message_info.contact_name,
                   contry_phone_code='221',  # À paramétrer selon le pays
                   phone_number=message_info.from_number[3:],
                   display_phone_number=message_info.from_number,
                   status='active'
               )
               self.logger.info(f"Nouvel utilisateur créé: {user.id}")

           return user

       except Exception as e:
           self.logger.error(f"Erreur lors de la gestion de l'utilisateur: {str(e)}")
           return None

   def _handle_conversation(self, user: User, channel: Channel, message_info: MessageData) -> Optional[ConversationData]:
       """Gère la logique de conversation"""
       try:
           # Obtenir ou créer channel_platform
           channel_platform = ChannelPlatform.objects.filter(
               channel=channel,
               platform_id=message_info.platform_id
           ).first()

           if not channel_platform:
               self.logger.error("Channel platform non trouvé")
               return None

           # Rechercher une conversation active existante
           conversation = Conversation.objects.filter(
               user=user,
               channel_platform=channel_platform,
               status='active'
           ).first()

           is_new = False
           current_step = None

           if not conversation:
               # Créer une nouvelle conversation
               conversation = Conversation.objects.create(
                   user=user,
                   channel_platform=channel_platform,
                   status='active',
                   handled_by=3  # Natural Language chatbot ID
               )
               is_new = True
           else:
               # Désactiver le step actif précédent
               current_step = ConversationStep.objects.filter(
                   conversation=conversation,
                   step_status='active'
               ).first()
               
               if current_step:
                   current_step.step_status = 'completed'
                   current_step.save()

           return ConversationData(
               conversation=conversation,
               current_step=current_step,
               is_new=is_new
           )

       except Exception as e:
           self.logger.error(f"Erreur lors de la gestion de la conversation: {str(e)}")
           return None

   def _save_message(self, conversation_data: ConversationData, message_info: MessageData) -> bool:
       """Sauvegarde le message et ses données associées"""
       try:
           # Calculer le nouveau step_number
           step_number = 1
           if not conversation_data.is_new and conversation_data.current_step:
               step_number = conversation_data.current_step.step_number + 1

           # Créer nouveau ConversationStep
           new_step = ConversationStep.objects.create(
               conversation=conversation_data.conversation,
               message_source=message_info.message_source,
               message_id_identified='Yes',
               option_step_id=1,  # À paramétrer selon la logique métier
               step_number=step_number,
               step_status='active'
           )

           # Créer MessageStatus
           MessageStatus.objects.create(
               conversation_step=new_step,
               id_from_api_whatsapp=message_info.message_id,
               status='received',
               timestamp=message_info.timestamp,
               recipient_id=message_info.from_number,
               type=message_info.type
           )

           # Si c'est un message texte, créer ConversationStepText
           if message_info.type == 'text':
               ConversationStepText.objects.create(
                   conversation_step=new_step,
                   text=message_info.content.get('body', '')
               )

           return True

       except Exception as e:
           self.logger.error(f"Erreur lors de la sauvegarde du message: {str(e)}")
           return False
