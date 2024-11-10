from django.db import models

class MessageStatus(models.Model):
    conversation_step = models.ForeignKey('ConversationStep', on_delete=models.CASCADE)
    id_from_api_whatsapp = models.CharField(max_length=255, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('read', 'Read'),
            ('failed', 'Failed'),
            ('received', 'Received')
        ],
        null=True
    )
    timestamp = models.CharField(max_length=255, null=True)
    recipient_id = models.CharField(max_length=20, null=True)
    pricing_model = models.CharField(max_length=10, null=True)
    category = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=10, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages_statuses'
        
    def __str__(self):
        return f"Status {self.status} for message {self.id_from_api_whatsapp}"
