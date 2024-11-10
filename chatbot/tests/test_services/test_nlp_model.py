import spacy

# Charger le modèle entraîné
nlp = spacy.load("output/model-last")

# Textes de test
texts = [
    "Je cherche un nouveau téléphone.",
    "Quel est le meilleur ordinateur portable ?",
    "Je veux acheter une montre connectée.",
    "Pouvez-vous me conseiller des chaussures de sport ?"
]

# Test du modèle
for text in texts:
    doc = nlp(text)
    print("\nTexte:", text)
    print("Entités trouvées:")
    for ent in doc.ents:
        print(f" - {ent.text} ({ent.label_})")
