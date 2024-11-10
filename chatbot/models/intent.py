from django.db import models

class Intent(models.Model):
    intent_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    priorite_affichage = models.IntegerField(default=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'intents'

class ResponseTemplate(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE)
    text = models.TextField()
    language = models.CharField(max_length=10, default='fr')
    priority = models.IntegerField(default=0)
    requires_context = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'responses_template'
