from django.db import models

class EntityDictionary(models.Model):
   text = models.CharField(max_length=255)
   entite = models.CharField(max_length=50)
   synonyms = models.TextField(null=True, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   class Meta:
       db_table = 'entities_dictionary'

class ResponseRule(models.Model):
   intent = models.ForeignKey('Intent', on_delete=models.CASCADE)
   response_template = models.ForeignKey('ResponseTemplate', on_delete=models.CASCADE)
   entity_conditions = models.TextField(null=True, blank=True)
   context_required = models.TextField(null=True, blank=True)
   priority = models.IntegerField(default=0)
   created_at = models.DateTimeField(auto_now_add=True)
   class Meta:
       db_table = 'responses_rules'

class Entity(models.Model):
   entity_name = models.CharField(max_length=255)
   description = models.TextField(null=True, blank=True)
   entity_type = models.CharField(
       max_length=100,
       choices=[
           ('Ecommerce', 'Ecommerce'),
           ('Standard', 'Standard')
       ]
   )
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   class Meta:
       db_table = 'entites'
   def __str__(self):
       return f"{self.entity_name} ({self.entity_type})"

class TextNormalization(models.Model):
   original_text = models.CharField(max_length=255, unique=True)
   normalized_text = models.CharField(max_length=255)
   type = models.CharField(max_length=50)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   class Meta:
       db_table = 'texts_normalization'
   def __str__(self):
       return f"{self.original_text} -> {self.normalized_text} ({self.type})"

class CacheRefreshLog(models.Model):
   timestamp = models.DateTimeField(auto_now_add=True)
   status = models.CharField(max_length=10)  # 'SUCCESS' ou 'ERROR'
   message = models.TextField()
   notification_email = models.BooleanField(default=False)
   notification_whatsapp = models.BooleanField(default=False)
   class Meta:
       db_table = 'cache_refresh_logs'
   def __str__(self):
       return f"{self.timestamp} - {self.status}"
