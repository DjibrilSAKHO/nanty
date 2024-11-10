import spacy
from typing import List, Dict, Any
from .text_preprocessor import TextPreprocessor
from chatbot.models.entity import Entity

class NLPService:
    def __init__(self):
        """Initialise le service NLP avec SpaCy et le préprocesseur"""
        try:
            self.nlp = spacy.load("fr_core_news_md")
        except OSError:
            print("Installation du modèle SpaCy français...")
            spacy.cli.download("fr_core_news_md")
            self.nlp = spacy.load("fr_core_news_md")
            
        self.preprocessor = TextPreprocessor()
        self.entities_cache = self._load_entities()

    def _load_entities(self) -> Dict[str, Dict[str, str]]:
        """Charge et catégorise les entités depuis la base de données"""
        categories = {
            'standard': {},
            'ecommerce': {},
            'requests': {}
        }
        
        for entity in Entity.objects.all():
            entity_type = entity.entity_type.lower()
            entity_name = entity.entity_name
            
            if entity_name.startswith('REQUEST_'):
                categories['requests'][entity_name] = entity_type
            elif entity_type == 'standard':
                categories['standard'][entity_name] = entity_type
            else:
                categories['ecommerce'][entity_name] = entity_type
                
        return categories

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrait toutes les entités du texte"""
        # Prétraitement
        normalized_text = self.preprocessor.preprocess(text)
        
        # Analyse SpaCy
        doc = self.nlp(normalized_text)
        
        # Extraction des entités
        entities = []
        for ent in doc.ents:
            # Chercher dans les différentes catégories
            entity_type = 'Unknown'
            for category, entities_dict in self.entities_cache.items():
                if ent.label_ in entities_dict:
                    entity_type = category
                    break

            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'type': entity_type,
                'start': ent.start_char,
                'end': ent.end_char
            })
            
        return entities
