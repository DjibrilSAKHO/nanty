import unittest
from django.test import TestCase
from chatbot.services.nlp_service import NLPService
from chatbot.models.entity import Entity

class TestNLPService(TestCase):
    def setUp(self):
        # Créer quelques entités de test
        Entity.objects.create(
            entity_name="PRODUCT",
            entity_type="Ecommerce",
            description="Product entity"
        )
        Entity.objects.create(
            entity_name="LOCATION",
            entity_type="Standard",
            description="Location entity"
        )
        Entity.objects.create(
            entity_name="REQUEST_FOR_PRICE",
            entity_type="Ecommerce",
            description="Price request"
        )
        
        self.nlp_service = NLPService()

    def test_entity_loading(self):
        """Test si les entités sont correctement chargées et catégorisées"""
        entities_cache = self.nlp_service.entities_cache
        
        # Vérifier la structure des catégories
        self.assertIn('standard', entities_cache)
        self.assertIn('ecommerce', entities_cache)
        self.assertIn('requests', entities_cache)
        
        # Vérifier la catégorisation
        self.assertIn('LOCATION', entities_cache['standard'])
        self.assertIn('PRODUCT', entities_cache['ecommerce'])
        self.assertIn('REQUEST_FOR_PRICE', entities_cache['requests'])

    def test_entity_extraction(self):
        """Test l'extraction d'entités d'un texte"""
        text = "Je veux un iPhone à Paris"
        entities = self.nlp_service.extract_entities(text)
        
        # Vérifier que nous avons des entités extraites
        self.assertTrue(len(entities) > 0)
        
        # Vérifier la structure des entités extraites
        for entity in entities:
            self.assertIn('text', entity)
            self.assertIn('label', entity)
            self.assertIn('type', entity)
            self.assertIn('start', entity)
            self.assertIn('end', entity)
