import re
from django.core.cache import cache
from chatbot.models.entity import TextNormalization

class TextPreprocessor:
   def __init__(self):
       # Charger uniquement depuis la BD
       self.load_normalizations()

   def load_normalizations(self):
       """Charge les normalisations depuis la BD avec cache"""
       self.normalizations = cache.get('text_normalizations')
       if self.normalizations is None:
           self.normalizations = {
               'abbreviation': {},
               'correction': {},
               'expression': {}
           }
           # Charger depuis la BD
           for norm in TextNormalization.objects.all():
               self.normalizations[norm.type][norm.original_text] = norm.normalized_text
           
           cache.set('text_normalizations', self.normalizations, timeout=3600)

   def normalize_spaces(self, text):
       """Normalise les espaces multiples"""
       return ' '.join(text.split())

   def normalize_price(self, text):
       """Normalise les formats de prix"""
       return re.sub(r'(\d+)\s*(?:FCFA|CFA|F)\b', r'\1 FCFA', text, flags=re.IGNORECASE)

   def apply_normalizations(self, text):
       """Applique toutes les normalisations dans l'ordre"""
       # Corrections orthographiques
       for original, normalized in self.normalizations['correction'].items():
           text = re.sub(r'\b' + re.escape(original) + r'\b', normalized, text, flags=re.IGNORECASE)
       
       # Abréviations
       for original, normalized in self.normalizations['abbreviation'].items():
           text = re.sub(r'\b' + re.escape(original) + r'\b', normalized, text, flags=re.IGNORECASE)
       
       # Expressions communes
       for original, normalized in self.normalizations['expression'].items():
           text = re.sub(r'\b' + re.escape(original) + r'\b', normalized, text, flags=re.IGNORECASE)

       # Traitement spécial pour "à"
       text = re.sub(r'\ba\b', 'à', text)
       
       return text

   def remove_duplicates(self, text):
       """Supprime les répétitions"""
       text = re.sub(r"c'est'est", "c'est", text)
       text = re.sub(r"à\s+à", "à", text)
       return text

   def preprocess(self, text):
       """Prétraitement principal du texte"""
       if not text:
           return text

       # Conversion en minuscules
       text = text.lower().strip()
       
       # Application des transformations dans l'ordre
       text = self.normalize_spaces(text)
       text = self.apply_normalizations(text)
       text = self.normalize_price(text)
       text = self.remove_duplicates(text)

       return text.strip()
