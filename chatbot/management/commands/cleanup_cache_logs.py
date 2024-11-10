from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from chatbot.models.entity import CacheRefreshLog

class Command(BaseCommand):
    help = 'Nettoie les logs de rafraîchissement de cache plus vieux qu\'une semaine'

    def handle(self, *args, **kwargs):
        try:
            # Calcul de la date limite (1 semaine)
            cutoff_date = timezone.now() - timedelta(days=7)
            
            # Suppression des vieux logs
            deleted_count = CacheRefreshLog.objects.filter(
                timestamp__lt=cutoff_date
            ).delete()[0]
            
            # Log du résultat
            self.stdout.write(
                self.style.SUCCESS(f'Nettoyage terminé : {deleted_count} logs supprimés')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors du nettoyage des logs : {str(e)}')
            )
