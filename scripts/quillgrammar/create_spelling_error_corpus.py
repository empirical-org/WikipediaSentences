import gzip
import spacy
import random
import json
from collections import defaultdict

MISSPELLING_FILE = "data/validated/birkbeck_misspellings.txt"
CORPUS_FILE = "/Users/yvespeirsman/Downloads/en.txt.gz"

nlp = spacy.load("en")

with open(MISSPELLING_FILE) as i:

    misspellings = defaultdict(lambda: [])
    current_word = None
    for line in i:
        line = line.strip()
        if line.startswith("$"):
            current_word = line[1:]
        elif current_word is not None:
            misspellings[current_word].append(line)

with gzip.open(CORPUS_FILE, "rb") as i:

    corpus = []

    sentences = [line.decode("utf-8") for line in i]
    random.shuffle(sentences)

    for sentence in sentences:

        if "(" in sentence:
            continue

        doc = nlp(sentence)
        for sentence in doc.sents:
            relevant_sentence = False
            corrections = []
            new_sentence = ""

            if len([_ for _ in sentence]) > 20:
                continue

            for token in sentence:

                if token.text in misspellings and len(corrections) == 0:
                    number_of_misspellings = len(misspellings[token.text])
                    new_token = random.choice([token.text]*number_of_misspellings*10 + misspellings[token.text])
                    new_sentence += new_token + token.whitespace_
                    relevant_sentence = True
                    if new_token != token.text:
                        corrections.append((token.text, new_token))
                else:
                    new_sentence += token.text_with_ws

            if relevant_sentence:
                corpus.append({"original_sentence": sentence.text.strip(),
                               "new_sentence": new_sentence.strip(),
                               "corrections": corrections})

        if len(corpus) >= 1000:
            break

    random.shuffle(corpus)

    with open("error_corpus.json", "w") as o:
        json.dump(corpus, o)