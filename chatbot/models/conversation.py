from django.db import models
from .base import User
from .channel import ChannelPlatform

class Conversation(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
   channel_platform = models.ForeignKey(ChannelPlatform, on_delete=models.CASCADE, null=False)
   handled_by = models.IntegerField(default=1, null=True)
   status = models.CharField(
       max_length=10,
       choices=[
           ('active', 'Active'),
           ('completed', 'Completed'),
           ('cancelled', 'Cancelled')
       ],
       default='active',
       null=True
   )
   current_context_id = models.PositiveBigIntegerField(null=True)
   session_data = models.TextField(null=True)
   created_at = models.DateTimeField(auto_now_add=True, null=False)
   updated_at = models.DateTimeField(auto_now=True, null=False)

   class Meta:
       db_table = 'conversations'

class ConversationStep(models.Model):
   conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=False)
   message_source = models.CharField(
       max_length=10,
       choices=[
           ('user', 'User'),
           ('chatbot', 'Chatbot'),
           ('operator', 'Operator')
       ],
       null=False
   )
   message_id_identified = models.CharField(
       max_length=3,
       choices=[
           ('Yes', 'Yes'),
           ('No', 'No'),
           ('NA', 'NA')
       ],
       default='No',
       null=False
   )
   option_step_id = models.PositiveIntegerField(null=False)
   step_number = models.IntegerField(null=False)
   step_status = models.CharField(
       max_length=10,
       choices=[
           ('active', 'Active'),
           ('completed', 'Completed'),
           ('skipped', 'Skipped')
       ],
       default='active',
       null=True
   )
   current_context_id = models.PositiveBigIntegerField(null=True)
   session_data = models.TextField(null=True)
   created_at = models.DateTimeField(auto_now_add=True, null=False)

   class Meta:
       db_table = 'conversations_steps'

class ConversationStepText(models.Model):
   conversation_step = models.ForeignKey(ConversationStep, on_delete=models.CASCADE, null=True)
   text = models.TextField(null=True)
   created_at = models.DateTimeField(auto_now_add=True, null=True)

   class Meta:
       db_table = 'conversations_steps_texts'
