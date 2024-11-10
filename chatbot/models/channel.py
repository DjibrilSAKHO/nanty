from django.db import models
from .base import Company, Platform

class Channel(models.Model):
   contry_code_number = models.CharField(max_length=3, null=False)
   phone_number = models.CharField(max_length=50, unique=True, null=False)
   display_phone_number = models.CharField(max_length=255, null=False)
   phone_number_id = models.CharField(max_length=255, null=False)
   company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False)
   status = models.CharField(
       max_length=8,
       choices=[
           ('Enabled', 'Enabled'),
           ('Disabled', 'Disabled')
       ],
       default='Enabled',
       null=False
   )

   class Meta:
       db_table = 'channels'

class ChannelPlatform(models.Model):
   channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=False)
   platform = models.ForeignKey(Platform, on_delete=models.CASCADE, null=False)

   class Meta:
       db_table = 'channels_platforms'
