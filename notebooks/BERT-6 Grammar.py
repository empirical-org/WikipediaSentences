#!/usr/bin/env python
# coding: utf-8

from quillnlp.models.bert.preprocessing import NLPTask, convert_data_to_input_items, get_data_loader

import ndjson
import random
import torch
import sys
import os
import json

TRAINING_FILES = ["/home/yves/projects/Quill-NLP-Tools-and-Datasets/notw.ndjson"]
#                  "/home/yves/projects/Quill-NLP-Tools-and-Datasets/subtitles.ndjson",
#                  "/home/yves/projects/Quill-NLP-Tools-and-Datasets/wiki_errors.ndjson"]
MAX_SEQ_LENGTH = 100
TRAIN_SIZE = 2000000
TEST_SIZE = 10000
BATCH_SIZE = 32
BASE_MODEL = "bert-base-cased"
MODEL_DIRECTORY = "/tmp/grammar"

data = []
for f in TRAINING_FILES:
    print(f)
    with open(f) as i:
        lines = ndjson.load(i)

    random.shuffle(lines)

    data.extend(lines[:int(TRAIN_SIZE/len(TRAINING_FILES))])


data = [{"text": item.get("synth_sentence", item.get("orig_sentence")), 
         "entities": item.get("entities", [])} for item in data]


label2idx = {"O": 0}

for sentence in data:
    if "entities" in sentence:
        for (_, _, label) in sentence["entities"]:
            if label not in label2idx:
                label2idx[label] = len(label2idx)
            
print(label2idx)
        

from transformers import BertForTokenClassification
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained(BASE_MODEL)
input_items = convert_data_to_input_items(data, label2idx, MAX_SEQ_LENGTH, tokenizer, NLPTask.SEQUENCE_LABELING)


random.shuffle(input_items)

test_items = input_items[-TEST_SIZE:]
valid_items = input_items[-2*TEST_SIZE:-TEST_SIZE]
train_items = input_items[:-2*TEST_SIZE]

test_dl = get_data_loader(test_items, BATCH_SIZE, task=NLPTask.SEQUENCE_LABELING, shuffle=False)
dev_dl = get_data_loader(valid_items, BATCH_SIZE, task=NLPTask.SEQUENCE_LABELING, shuffle=False)
train_dl = get_data_loader(train_items, BATCH_SIZE, task=NLPTask.SEQUENCE_LABELING, shuffle=True)


sys.path.append('../')

from quillnlp.models.bert.train import train
from transformers import BertModel

model = BertForTokenClassification.from_pretrained(BASE_MODEL, num_labels=len(label2idx))
model.to("cuda")

config = {"labels": label2idx, "base_model": BASE_MODEL, "max_seq_length": MAX_SEQ_LENGTH}
with open(os.path.join(MODEL_DIRECTORY, "config.json"), "w") as o:
    json.dump(config, o)

train(model, train_dl, dev_dl, BATCH_SIZE, 32/BATCH_SIZE, device="cuda",
      num_train_epochs=10, patience=2, eval_frequency=5000, output_dir=MODEL_DIRECTORY)


# In[8]:


from quillnlp.models.bert.train import evaluate

output_model_file = "/tmp/model.bin"
print("Loading model from", output_model_file)
device="cpu"

model_state_dict = torch.load(output_model_file, map_location=lambda storage, loc: storage)
model = BertForTokenClassification.from_pretrained("bert-base-cased", state_dict=model_state_dict, num_labels=len(label2idx))
model.to(device)

#_, train_correct, train_predicted = evaluate(model, train_dataloader)
#_, dev_correct, dev_predicted = evaluate(model, dev_dataloader)
_, _, test_correct, test_predicted = evaluate(model, test_dl, device)


# In[9]:


idx2label = {v:k for k,v in label2idx.items()}

for item, correct, predicted in zip(test_items, test_correct, test_predicted):
    print(item.text)
    for error in set(predicted):
        print("Found:", idx2label[error])
    for error in set(correct):
        print("Correct:", idx2label[error])
    


# In[10]:


# Read error input

error_map = {'POSSESSIVE': 'Plural versus possessive nouns', 
             'VERB': 'Subject-verb agreement', 
             'ADV': 'Adverbs versus adjectives', 
             'ITS': "Its versus it's", 
             'THEN': 'Than versus then'}

data = []
with open("tests/data/grammar_valid.tsv") as i:
    for line in i:
        line = line.strip().split("\t")
        if len(line) == 3:
            data.append(line)

results = {}
for (error_type, correct_sentence, incorrect_sentence) in data:
    if error_type not in results:
        results[error_type] = {"cc": 0, "ci": 0, "ic": 0, "ii": 0}

    correct_features = convert_data_to_input_items([{"text": correct_sentence}], 
                                                     label2idx, MAX_SEQ_LENGTH, tokenizer, NLPTask.SEQUENCE_LABELING)

    incorrect_features = convert_data_to_input_items([{"text": incorrect_sentence}],
                                                       label2idx, MAX_SEQ_LENGTH, tokenizer, NLPTask.SEQUENCE_LABELING)

    correct_dl = get_data_loader(correct_features, 1, task=NLPTask.SEQUENCE_LABELING, shuffle=False)
    incorrect_dl = get_data_loader(incorrect_features, 1, task=NLPTask.SEQUENCE_LABELING, shuffle=False)
    
    _, _, _, correct_predicted = evaluate(model, correct_dl, device)
    _, _, _, incorrect_predicted = evaluate(model, incorrect_dl, device)
        
    errors = [idx2label[i] for i in set(correct_predicted[0])]
    errors = [error_map[e] for e in errors if e in error_map]
    print(correct_sentence)
    print(errors)

    if len(errors) == 0:
        results[error_type]["cc"] += 1
    else:
        results[error_type]["ci"] += 1

    errors = [idx2label[i] for i in set(incorrect_predicted[0])]
    errors = [error_map[e] for e in errors if e in error_map]
    print(incorrect_sentence)
    print(errors)

    if len(errors) == 0:
        results[error_type]["ic"] += 1
    else:
        results[error_type]["ii"] += 1


# In[11]:


print(results)


# In[12]:


for error_type in results:
    correct = results[error_type]["cc"] + results[error_type]["ii"]
    incorrect = results[error_type]["ic"] + results[error_type]["ci"]

    precision = results[error_type]["cc"]/ (results[error_type]["cc"] + results[error_type]["ic"])
    recall = results[error_type]["cc"] / (results[error_type]["cc"] + results[error_type]["ci"])
    fscore = 2*precision*recall/(precision+recall)

    print(error_type, precision, recall, fscore)


# In[ ]:




