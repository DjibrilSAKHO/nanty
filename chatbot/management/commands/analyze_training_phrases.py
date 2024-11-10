from django.core.management.base import BaseCommand
from django.core.management import CommandParser
from django.core.management.base import BaseCommand
from django.db.models import Count
from chatbot.models.entity import TextNormalization
from django.db import connection
import re
from collections import Counter

class Command(BaseCommand):
    help = 'Analyse les phrases d\'entraînement pour générer des normalisations'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dictionnaire des traductions wolof
        self.wolof_translations = {
            'amoul': 'il n\'y a pas',
            'nga': 'tu es',
            'nak': 'alors',
            'dem': 'aller',
            'waw': 'oui',
            'rek': 'seulement',
            'moy': 'c\'est',
            'nio': 'c\'est ça',
            'yaw': 'toi',
            'kay': 'viens',
            'ak': 'et',
            'bi': 'le/la',
            'bou': 'qui',
            'deh': 'vraiment',
            'mou': 'il/elle',
            'yi': 'les',
            'ba': 'jusqu\'à',
            'bii': 'celui-ci/celle-ci',
            'wa': 'les gens de',
            'waa': 'les gens',
            'fan': 'où',
            'lay': 'va',
            'nek': 'être',
            'kon': 'donc'
        }

        # Dictionnaire des salutations
        self.greetings_translations = {
            'bjr': 'bonjour',
            'slt': 'salut', 
            'cc': 'coucou',
            'bsr': 'bonsoir',
            'hi': 'salut'
        }

        # Dictionnaire des expressions composées
        self.compound_expressions = {
            'est-ce': 'est-ce que',
            'est-il': 'est-il',
            'vas-tu': 'vas-tu',
            'n\'est': 'n\'est',
            'c\'est': 'c\'est',
            'y\'a': 'il y a',
            's\'il': 's\'il',
            't\'il': 't-il'
        }

        # Dictionnaire des abréviations courantes
        self.common_abbreviations = {
            'svp': 's\'il vous plaît',
            'stp': 's\'il te plaît',
            'vs': 'vous',
            'rdv': 'rendez-vous',
            'bcp': 'beaucoup',
            'ms': 'mais',
            'bn': 'bien',
            'kel': 'quel',
            'esk': 'est-ce que',
            'nn': 'non',
            'koi': 'quoi',
            'oki': 'ok',
            'fo': 'faut',
            'g': 'j\'ai',
            'c': 'c\'est',
            'cv': 'ça va',
            'mme': 'madame',
            'mr': 'monsieur',
            'ref': 'référence'
        }

        # Dictionnaire des contractions
        self.contractions = {
            'jai': 'j\'ai',
            'tas': 'tu as',
            'tes': 'tu es',
            'chui': 'je suis',
            'chuis': 'je suis',
            'jsuis': 'je suis',
            'jvais': 'je vais',
            'jve': 'je veux',
            'jpeux': 'je peux',
            'jcrois': 'je crois'
        }

        # Dictionnaire des formes avec apostrophe
        self.apostrophe_forms = {
            "c'": "c'est",
            "j'": "je",
            "d'": "de",
            "l'": "le",
            "n'": "ne",
            "m'": "me",
            "s'": "se",
            "qu'": "que",
            "t'": "te",
            "y'": "il y",
            "aujourd'": "aujourd'hui",
            "jusqu'": "jusque",
            "quelqu'": "quelque"
        }

        # Normalisation des ponctuations
        self.punctuation_normalizations = {
            'ok,': 'ok',
            'ok.': 'ok',
            'd\'accord.': 'd\'accord',
            'd\'accord,': 'd\'accord',
            'oui,': 'oui',
            'non,': 'non',
            'svp?': 'svp',
            'stp?': 'stp',
            'mme,': 'madame',
            'mr,': 'monsieur',
            'ref:': 'référence'
        }

        # Mots à ignorer
        self.ignore_words = set([
            'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'de', 'du',
            'en', 'dans', 'par', 'sur', 'pour', 'avec', 'sans', 'sous',
            'a', 'à', 'y', 'est', 'sont', 'ont', 'ce', 'se', 'ne', 'pas',
            'au', 'aux', 'ces', 'ses', 'mes', 'tes', 'nos', 'vos'
        ])

        # Set des mots wolof pour vérification rapide
        self.wolof_words = set(self.wolof_translations.keys())

    def add_arguments(self, parser) -> None:
        """Configure les arguments de la commande"""
        parser.add_argument(
            '--min-frequency',
            dest='min_frequency',
            type=int,
            default=3,
            help='Fréquence minimum pour considérer un pattern'
        )
        parser.add_argument(
            '--start-id',
            dest='start_id',
            type=int,
            default=111,
            help='ID de début pour l\'analyse'
        )
        parser.add_argument(
            '--save',
            dest='save',
            action='store_true',
            default=False,
            help='Sauvegarder les normalisations dans la base de données'
        )

    def clean_text(self, text):
        """Nettoie et normalise le texte"""
        # Nettoyage de base
        text = text.lower().strip()

        # Standardise les apostrophes
        text = text.replace("'", "'").replace("`", "'")

        # Nettoie la ponctuation finale
        text = re.sub(r'[.,!?]+$', '', text)

        # Nettoie les espaces multiples
        text = ' '.join(text.split())

        return text

    def extract_apostrophe_forms(self, text):
        """Extrait les formes avec apostrophe d'un texte"""
        apostrophe_pattern = re.compile(r"\b\w+'|\b\w+'[a-z]+")
        matches = apostrophe_pattern.finditer(text)
        return [match.group() for match in matches]

    def find_patterns(self, phrases):
        """Analyse différents types de patterns"""
        results = {
            'potential_abbreviations': Counter(),
            'wolof_expressions': Counter(),
            'greetings': Counter(),
            'punctuation_variations': Counter(),
            'contractions': Counter(),
            'apostrophe_forms': Counter(),
            'compound_expressions': Counter()
        }

        for phrase in phrases:
            phrase_clean = self.clean_text(phrase)

            # Vérification des variations de ponctuation
            if phrase.lower().strip() in self.punctuation_normalizations:
                results['punctuation_variations'][phrase.lower().strip()] += 1

            # Extraction des formes avec apostrophe
            apostrophe_forms = self.extract_apostrophe_forms(phrase_clean)
            results['apostrophe_forms'].update(apostrophe_forms)

            # Analyse des mots et expressions
            words = phrase_clean.split()
            for word in words:
                # Nettoyage du mot
                word = word.strip()

                # Expressions composées
                if word in self.compound_expressions:
                    results['compound_expressions'][word] += 1
                    continue

                # Contractions
                if word in self.contractions:
                    results['contractions'][word] += 1
                    continue

                # Expressions wolof
                if word in self.wolof_words:
                    results['wolof_expressions'][word] += 1
                # Salutations
                elif word in self.greetings_translations:
                    results['greetings'][word] += 1
                # Abréviations
                elif re.compile(r'\b[A-Za-z\']{1,3}\b').match(word) and word not in self.ignore_words:
                    results['potential_abbreviations'][word] += 1

        return results

    def get_normalization_type(self, original_text, normalized_text):
        """Détermine le type de normalisation approprié"""
        if original_text in self.greetings_translations:
            return 'greeting'
        if original_text in self.wolof_words:
            return 'local_expression'
        if original_text in self.punctuation_normalizations:
            return 'punctuation'
        if original_text in self.apostrophe_forms:
            return 'contraction'
        if original_text in self.compound_expressions:
            return 'expression'
        if original_text in self.common_abbreviations:
            return 'abbreviation'
        if original_text in self.contractions:
            return 'contraction'
        return 'correction'

    def save_normalizations(self, results, min_frequency):
        """Sauvegarde les normalisations détectées"""
        normalizations_to_add = []

        # Traitement des formes avec apostrophe
        for form, count in results['apostrophe_forms'].items():
            if count >= min_frequency:
                cleaned_form = form.replace("\\", "")  # Nettoie la forme
                if cleaned_form in self.apostrophe_forms:
                    normalizations_to_add.append({
                        'original_text': cleaned_form,
                        'normalized_text': self.apostrophe_forms[cleaned_form],
                        'type': 'contraction'
                    })

        # Traitement des expressions wolof
        for pattern, count in results['wolof_expressions'].items():
            if count >= min_frequency and pattern in self.wolof_translations:
                normalizations_to_add.append({
                    'original_text': pattern,
                    'normalized_text': self.wolof_translations[pattern],
                    'type': 'local_expression'
                })

        # Traitement des salutations
        for pattern, count in results['greetings'].items():
            if count >= min_frequency and pattern in self.greetings_translations:
                normalizations_to_add.append({
                    'original_text': pattern,
                    'normalized_text': self.greetings_translations[pattern],
                    'type': 'greeting'
                })

        # Traitement des expressions composées
        for pattern, count in results['compound_expressions'].items():
            if count >= min_frequency and pattern in self.compound_expressions:
                normalizations_to_add.append({
                    'original_text': pattern,
                    'normalized_text': self.compound_expressions[pattern],
                    'type': 'expression'
                })

        # Traitement des abréviations
        for pattern, count in results['potential_abbreviations'].items():
            if count >= min_frequency and pattern in self.common_abbreviations:
                normalizations_to_add.append({
                    'original_text': pattern,
                    'normalized_text': self.common_abbreviations[pattern],
                    'type': 'abbreviation'
                })

        # Traitement des contractions
        for pattern, count in results['contractions'].items():
            if count >= min_frequency and pattern in self.contractions:
                normalizations_to_add.append({
                    'original_text': pattern,
                    'normalized_text': self.contractions[pattern],
                    'type': 'contraction'
                })

        # Sauvegarde dans la base de données
        saved_count = 0
        skipped_count = 0
        error_count = 0

        for norm in normalizations_to_add:
            try:
                obj, created = TextNormalization.objects.get_or_create(
                    original_text=norm['original_text'],
                    defaults={
                        'normalized_text': norm['normalized_text'],
                        'type': norm['type']
                    }
                )
                if created:
                    self.stdout.write(f"Ajouté: {norm['original_text']} -> {norm['normalized_text']} ({norm['type']})")
                    saved_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(
                    f"Erreur lors de la sauvegarde de {norm['original_text']}: {str(e)}"
                ))

        return {
            'saved': saved_count,
            'skipped': skipped_count,
            'errors': error_count
        }

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT phrase
                FROM training_phrases
                WHERE id >= %s
                AND phrase IS NOT NULL
                AND phrase != ''
            """, [options['start_id']])
            phrases = [row[0] for row in cursor.fetchall()]

        self.stdout.write(f"Analyse de {len(phrases)} phrases...")

        results = self.find_patterns(phrases)

        # Affichage des résultats par catégorie
        categories = {
            'Abréviations potentielles': 'potential_abbreviations',
            'Expressions en Wolof': 'wolof_expressions',
            'Formules de salutation': 'greetings',
            'Variations de ponctuation': 'punctuation_variations',
            'Contractions': 'contractions',
            'Formes avec apostrophe': 'apostrophe_forms',
            'Expressions composées': 'compound_expressions'
        }

        for title, category in categories.items():
            self.stdout.write(f"\n{title}:")
            if category == 'apostrophe_forms':
                for form, count in results[category].most_common():
                    if count >= options['min_frequency']:
                        clean_form = form.replace('\\', '')
                        self.stdout.write(f"{clean_form}: {count} occurrences")
            else:
                for pattern, count in results[category].most_common():
                    if count >= options['min_frequency']:
                        self.stdout.write(f"{pattern}: {count} occurrences")

        if options['save']:
            self.stdout.write("\nSauvegarde des normalisations...")
            save_results = self.save_normalizations(results, options['min_frequency'])
            self.stdout.write(self.style.SUCCESS(
                f"\nRésultats de la sauvegarde :"
                f"\n - {save_results['saved']} nouvelles normalisations ajoutées"
                f"\n - {save_results['skipped']} normalisations existantes ignorées"
                f"\n - {save_results['errors']} erreurs rencontrées"
            ))
