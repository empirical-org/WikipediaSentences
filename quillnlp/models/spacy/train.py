import json
import logging
import operator
import os
import random
import time
from pathlib import Path

import ndjson
import spacy
from spacy.util import minibatch, compounding
from tqdm import tqdm


logging.getLogger().setLevel(logging.INFO)


def preprocess_item(item, idx2label, lang):
    """
    Preprocesses a data item to the format required by spaCy.

    Args:
        item: the json data item with a title and probabilities
        config: the json config with information about the field names
        lang: the language of the item

    Returns: the item in spaCy format

    """

    cats = {}
    if "probabilities" in item:
        for i, prob in enumerate(item["probabilities"]):
            cats[idx2label[i]] = prob
    elif "label" in item:
        for label in idx2label.values():
            cats[label] = 0.0
        cats[item["label"]] = 1.0

    return item["text"], {"cats": cats}



def pick_highest_category(d):
    """
    Finds the key with the highest value in a dictionary.

    Args:
        d: the input dictionary with numbers as values

    Returns: the key with the highest value

    """
    return max(d.items(), key=operator.itemgetter(1))[0]


def evaluate(model, data):
    """
    Evaluates a trained model on a dataset.

    Args:
        model: the model to be evaluated
        data: the data on which to evaluate the model

    Returns: the accuracy and off-by-1 accuracy of the model. The
        off-by-1 accuracy is the proportion of items with the correct
        rating or a rating that is off by only 1.

    """
    docs = (model(item[0]) for item in data)
    correct = 0
    for i, doc in enumerate(docs):
        gold = data[i][1]["cats"]

        # print(gold)
        # print(doc.cats)

        correct_cat = pick_highest_category(gold)
        predicted_cat = pick_highest_category(doc.cats)

        # print(correct_cat)
        # print(predicted_cat)
                
        if correct_cat == predicted_cat:
            correct += 1

    acc = correct / len(data)
    return {"acc": acc}


def train_language(train_data, dev_data, test_data, idx2label, lang, output_dir):
    """
    Trains a spaCy model for a given language and saves it.

    Args:
        lang: the language
        output_dir: the output directory

    Returns: the accuracy and off-by-1 accuracy for the model

    """
    logging.info(f"Start training for {lang}")

    spacy.prefer_gpu()

    nlp = spacy.load(lang)

    textcat = nlp.create_pipe(
        "textcat",
        config={
            "exclusive_classes": False,
            "architecture": "ensemble"
        }
    )

    nlp.add_pipe(textcat, last=True)

    for label in idx2label.values():
        textcat.add_label(label)

    train_data = [preprocess_item(item, idx2label, lang) for item in train_data]
    dev_data = [preprocess_item(item, idx2label, lang) for item in dev_data]
    test_data = [preprocess_item(item, idx2label, lang) for item in test_data]

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'textcat']

    history = []
    patience = 2
    max_iter = 20
    with nlp.disable_pipes(*other_pipes):  # only train textcat
        optimizer = nlp.begin_training()
        batch_sizes = compounding(4., 32., 1.001)
        for i in range(max_iter):
            losses = {}
            # batch up the examples using spaCy's minibatch
            random.shuffle(train_data)
            batches = minibatch(train_data, size=batch_sizes)
            for batch in tqdm(batches):
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.2, losses=losses)

            with textcat.model.use_params(optimizer.averages):
                scores = evaluate(nlp, dev_data)
            logging.info('{0:.3f}\t{1:.3f}'.format(losses['textcat'], scores['acc']))
            history.append(scores['acc'])

            if scores['acc'] == max(history):
                if output_dir is not None:
                    output_dir = Path(output_dir)
                    if not output_dir.exists():
                        output_dir.mkdir()
                    nlp.to_disk(output_dir)
                    logging.info("Saved model to {}".format(output_dir))

            if max(history) > max(history[-patience:]):
                break

    logging.info("Loading best model")
    nlp = spacy.load(output_dir)

    scores = evaluate(nlp, test_data)

    logging.info("Final accuracy: {0:.3f}".format(scores["acc"]))

    return {"acc": scores["acc"]}