# Nanty - Résumé Technique Complet

## 1. Informations Générales
- **Nom du projet** : Nanty
- **Description** : Chatbot E-commerce multicanal et multilingue
- **État actuel** : DEV
- **Stack technique** :
  * Python 3.10.12
  * Django 5.1.2
  * MySQL (nantydb)
  * Spacy (fr_core_news_md)
  * ResNet50
- **URL** : nanty.net

## 2. État du Développement
### Progression
- **Dernière tâche complétée** : Normalisation des messages
- **Tâche en cours** : Intégration de Spacy
- **Prochaines étapes** : 
  * Analyse Spacy des messages WhatsApp
  * Traitement des réponses
  * Tests d'intégration

### Canaux de Messagerie
- **Actif** : WhatsApp
- **En développement** : WhatsApp (phase 1)
- **Configuration** : Webhook WhatsApp configuré

## 3. Architecture Technique

### Structure du Projet
```
nanty/
├── chatbot/           # App principale du chatbot
│   ├── models/       # Modèles de données
│   ├── services/     # Services NLP et messages
│   ├── views/        # Webhooks et API
│   └── management/   # Commandes personnalisées
├── main/             # Interface utilisateur
└── config/           # Configurations
```

### Base de Données
#### Modèles Principaux
1. **Gestion Utilisateurs**
   - User (chatbot, client, operator, system, founder)
   - Company
   - SubscriptionType

2. **Communication**
   - Channel
   - Platform
   - ChannelPlatform

3. **Conversations**
   - Conversation
   - ConversationStep
   - MessageStatus

4. **NLP**
   - Intent
   - Entity
   - ResponseTemplate
   - TextNormalization

## 4. Pipeline de Traitement

### Réception des Messages
1. **Webhook WhatsApp** (`/api/webhook/whatsapp/`)
   - Vérification du token
   - Traitement synchrone
   - Transaction atomique

### Prétraitement
1. **Normalisation** (TextPreprocessor)
   - Espaces et casse
   - Abréviations
   - Expressions locales (Wolof)
   - Prix et formats

2. **Cache**
   - Système : Redis
   - Durée : 3600s
   - Types : abréviations, corrections, expressions

### Traitement NLP
1. **Configuration Spacy**
   - Modèle : fr_core_news_md
   - Pipeline : tok2vec, ner
   - Batch size : 1000

2. **Composants**
   - Tok2Vec (MultiHashEmbed)
   - NER (TransitionBasedParser)

### Gestion des Conversations
1. **États**
   - Messages : sent, delivered, read, failed, received
   - Conversations : active, completed, cancelled
   - Étapes : active, completed, skipped

2. **Contexte**
   - Session utilisateur
   - Données de contexte
   - Règles de réponses

## 5. Configurations et Accès
- Base de données : Configuration dans .env
- API WhatsApp : Webhook configuré
- Cache : Redis

## 6. Points d'Attention
### Performance
- Cache des normalisations
- Transactions atomiques
- Batch processing NLP

### Monitoring
- Logs de cache
- Statuts des messages
- Suivis des conversations

### Multilingue
- Support français principal
- Intégration Wolof
- Templates multilingues

## 7. Commandes de Maintenance
```bash
# Analyse des phrases
python manage.py analyze_training_phrases

# Nettoyage cache
python manage.py cleanup_cache_logs

# Actualisation normalisations
python manage.py refresh_text_normalizations_cache
```

---

Pour commencer une nouvelle tâche, assurez-vous de :
1. Vérifier l'état des migrations
2. Actualiser le cache des normalisations
3. Consulter les logs récents
4. Valider les configurations WhatsApp

Documentation complète et code source disponibles dans le projet.

## Historique des Mises à Jour
- 10/11/2024 : Ajout de la section gestion du code source
  * Documentation de la configuration Git
  * Documentation du workflow de mise à jour
  * Documentation de la structure des commits
- 10/11/2024 : Version initiale du résumé
  * Documentation de l'architecture complète
  * Documentation du pipeline NLP
  * Documentation de l'intégration WhatsApp
  * Documentation des modèles et des composants
  * Documentation des commandes de maintenance

## Comment Utiliser ce Résumé
1. Consultez ce fichier au début de chaque nouvelle session de développement
2. Mettez à jour les sections pertinentes après des changements significatifs
3. Ajoutez les nouvelles mises à jour dans la section "Historique des Mises à Jour"
4. Commitez les changements avec le message "docs: update project summary"

## Conventions de Mise à Jour
- Datez chaque modification dans l'historique
- Gardez les sections organisées et formatées
- Mettez à jour la date en haut du document
- Vérifiez la cohérence des informations
- Utilisez ./update_summary_date.sh pour mettre à jour la date

## 8. Gestion du Code Source
### Git
- **Configuration** :
  * Branch principale : main
  * .gitignore configuré pour Python/Django
  * Alias configuré : update-summary

### Workflow de Mise à Jour
1. **Documentation** :
   - Script update_summary_date.sh pour la mise à jour des dates
   - Commande `git update-summary` pour commiter les changements

2. **Fichiers Exclus** :
   - Fichiers Python compilés (__pycache__/)
   - Base de données locale (db.sqlite3)
   - Environnement virtuel (venv/)
   - Dossiers spécifiques (backups/, output/, corpus/)
   - Fichiers de données (*.jsonl, *.sql)
   - Fichiers d'environnement (.env)

3. **Structure des Commits** :
   - docs: pour la documentation
   - feat: pour les nouvelles fonctionnalités
   - fix: pour les corrections de bugs
   - chore: pour la maintenance
