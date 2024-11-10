from django.test import TestCase
from unittest.mock import patch
from django.core.cache import cache
from chatbot.services.text_preprocessor import TextPreprocessor

class TextPreprocessorTests(TestCase):
    def setUp(self):
        # Nettoyer le cache
        cache.clear()
        
        # Créer l'instance avec un mock direct
        patcher = patch.object(TextPreprocessor, 'load_normalizations', autospec=True)
        self.mock_load = patcher.start()
        self.addCleanup(patcher.stop)
        
        # Créer l'instance
        self.preprocessor = TextPreprocessor()
        
        # Définir les normalisations directement
        self.preprocessor.normalizations = {
            'abbreviation': {
                'bsr': 'bonjour',
                'bjr': 'bonjour'
            },
            'correction': {
                'bvonjour': 'bonjour'
            },
            'expression': {
                'c': "c'est",
                'c a': "c'est à"
            }
        }

    def test_preprocess(self):
        test_cases = [
            # Test des abréviations
            ("Bsr chaussures", "bonjour chaussures"),
            ("bjr comment allez vous", "bonjour comment allez vous"),
            
            # Test des corrections orthographiques
            ("bvonjour", "bonjour"),
            
            # Test des expressions
            ("c bon", "c'est bon"),
            ("c a combien", "c'est à combien"),
            
            # Test des prix
            ("ça coûte 8500FCFA", "ça coûte 8500 FCFA"),
            ("prix: 1000 F", "prix: 1000 FCFA"),
            
            # Test des espaces
            ("bonjour    monde", "bonjour monde"),
            
            # Test combinés
            ("bsr  c   8500F", "bonjour c'est 8500 FCFA"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                processed = self.preprocessor.preprocess(input_text)
                self.assertEqual(processed, expected)
