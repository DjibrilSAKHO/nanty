import spacy
import json
from spacy.tokens import DocBin
from tqdm import tqdm
import random

def load_data(file_path):
    training_data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            example = json.loads(line)
            text = example['text']
            entities = []
            # Convertir les spans en format spaCy
            for span in example['spans']:
                entities.append((span['start'], span['end'], span['label']))
            training_data.append((text, {'entities': entities}))
    return training_data

def prepare_training(data, split=0.8):
    # Mélanger les données
    random.shuffle(data)
    split_point = int(len(data) * split)
    return data[:split_point], data[split_point:]

def main():
    print("Chargement du modèle de base...")
    nlp = spacy.load('fr_core_news_md')
    
    print("Chargement des données...")
    data = load_data('fr_core_news_md_dataset_annotations_finales.jsonl')
    train_data, eval_data = prepare_training(data)
    
    print(f"Nombre d'exemples d'entraînement: {len(train_data)}")
    print(f"Nombre d'exemples d'évaluation: {len(eval_data)}")
    
    # Préparer les données d'entraînement
    train_db = DocBin()
    for text, annots in tqdm(train_data, desc="Préparation des données d'entraînement"):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annots['entities']:
            span = doc.char_span(start, end, label=label)
            if span:
                ents.append(span)
        doc.ents = ents
        train_db.add(doc)
    
    # Préparer les données d'évaluation
    eval_db = DocBin()
    for text, annots in tqdm(eval_data, desc="Préparation des données d'évaluation"):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annots['entities']:
            span = doc.char_span(start, end, label=label)
            if span:
                ents.append(span)
        doc.ents = ents
        eval_db.add(doc)
    
    print("Sauvegarde des données...")
    train_db.to_disk("./corpus/train.spacy")
    eval_db.to_disk("./corpus/eval.spacy")
    print("Terminé!")

if __name__ == "__main__":
    main()
