from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone
from chatbot.models.entity import TextNormalization, CacheRefreshLog

class Command(BaseCommand):
    help = 'Rafraîchit le cache des normalisations de texte'

    def send_notification(self, success, error_message=None):
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        if success:
            subject = f'[Nanty] Cache rafraîchi avec succès - {timestamp}'
            message = 'Le cache des normalisations a été mis à jour avec succès.'
        else:
            subject = f'[Nanty] ERREUR rafraîchissement cache - {timestamp}'
            message = f'Erreur lors de la mise à jour du cache : {error_message}'

        try:
            send_mail(
                subject,
                message,
                'sakhodjibril76@gmail.com',
                ['sakhodjibril76@gmail.com', 'sakhodjibril76@gmail.com'],
                fail_silently=False,
            )
            notification_email = True
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erreur envoi email : {str(e)}'))
            notification_email = False

        return notification_email

    def handle(self, *args, **kwargs):
        try:
            # Nettoyage du cache existant
            cache.delete('text_normalizations')
            self.stdout.write('Cache des normalisations nettoyé')
            
            # Rechargement des données
            normalizations = {
                'abbreviation': {},
                'correction': {},
                'expression': {}
            }
            for norm in TextNormalization.objects.all():
                normalizations[norm.type][norm.original_text] = norm.normalized_text
            
            # Mise en cache des nouvelles données
            cache.set('text_normalizations', normalizations, timeout=3600)
            self.stdout.write(self.style.SUCCESS('Cache des normalisations mis à jour avec succès'))
            
            # Envoyer notification de succès et logger
            notification_sent = self.send_notification(success=True)
            CacheRefreshLog.objects.create(
                status='SUCCESS',
                message='Cache mis à jour avec succès',
                notification_email=notification_sent
            )
            
        except Exception as e:
            error_message = str(e)
            self.stdout.write(self.style.ERROR(f'Erreur lors de la mise à jour du cache : {error_message}'))
            
            # Envoyer notification d'erreur et logger
            notification_sent = self.send_notification(success=False, error_message=error_message)
            CacheRefreshLog.objects.create(
                status='ERROR',
                message=error_message,
                notification_email=notification_sent
            )
