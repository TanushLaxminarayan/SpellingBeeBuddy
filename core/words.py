# core/words.py
import csv
import random

def load_words():
    words = []
    with open("practice_words.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            words.append({
                "word": row["word"].lower(),
                "difficulty": row.get("difficulty", "medium"),
                "definition": row.get("definition", ""),
                "sentence": row.get("sentence", ""),
                "pronunciation": row.get("pronunciation", "")
            })
    random.shuffle(words)
    return words
