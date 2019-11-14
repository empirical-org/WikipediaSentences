#!/usr/bin/env python
# coding: utf-8

# # First BERT Experiments
# 
# In this notebook we do some first experiments with BERT: we finetune a BERT model+classifier on each of our datasets separately and compute the accuracy of the resulting classifier on the test data.

# For these experiments we use the `pytorch_transformers` package. It contains a variety of neural network architectures for transfer learning and pretrained models, including BERT and XLNET.
# 
# Two different BERT models are relevant for our experiments: 
# 
# - BERT-base-uncased: a relatively small BERT model that should already give reasonable results,
# - BERT-large-uncased: a larger model for real state-of-the-art results.

# In[1]:


BERT_MODEL = 'bert-base-uncased'
BATCH_SIZE = 16 if "base" in BERT_MODEL else 2
GRADIENT_ACCUMULATION_STEPS = 1 if "base" in BERT_MODEL else 8
MAX_SEQ_LENGTH = 100
PREFIX = "eatingmeat_but_large_ginger"


# ## Data
# 
# We use the same data as for all our previous experiments. Here we load the training, development and test data for a particular prompt.

# In[2]:


import sys
sys.path.append('../')

import ndjson
import glob

from quillnlp.models.bert.preprocessing import preprocess, create_label_vocabulary

train_file = f"../data/interim/{PREFIX}_train_withprompt.ndjson"
synth_files = glob.glob(f"../data/interim/{PREFIX}_train_withprompt_*.ndjson")
dev_file = f"../data/interim/{PREFIX}_dev_withprompt.ndjson"
test_file = f"../data/interim/{PREFIX}_test_withprompt.ndjson"

with open(train_file) as i:
    train_data = ndjson.load(i)

synth_data = []
for f in synth_files:
    if "allsynth" in f:
        continue
    with open(f) as i:
        synth_data += ndjson.load(i)
    
with open(dev_file) as i:
    dev_data = ndjson.load(i)
    
with open(test_file) as i:
    test_data = ndjson.load(i)
    
label2idx = create_label_vocabulary(train_data)
idx2label = {v:k for k,v in label2idx.items()}
target_names = [idx2label[s] for s in range(len(idx2label))]

train_dataloader = preprocess(train_data, BERT_MODEL, label2idx, MAX_SEQ_LENGTH, BATCH_SIZE)
dev_dataloader = preprocess(dev_data, BERT_MODEL, label2idx, MAX_SEQ_LENGTH, BATCH_SIZE)
test_dataloader = preprocess(test_data, BERT_MODEL, label2idx, MAX_SEQ_LENGTH, BATCH_SIZE, shuffle=False)


# ## Model

# In[3]:


import torch
from quillnlp.models.bert.models import get_bert_classifier

device = "cuda" if torch.cuda.is_available() else "cpu"
model = get_bert_classifier(BERT_MODEL, len(label2idx), device=device)


# ## Training

# In[4]:


from quillnlp.models.bert.train import train

output_model_file = train(model, train_dataloader, dev_dataloader, BATCH_SIZE, GRADIENT_ACCUMULATION_STEPS, device)


# ## Evaluation

# In[5]:


from quillnlp.models.bert.train import evaluate
from sklearn.metrics import precision_recall_fscore_support, classification_report

print("Loading model from", output_model_file)
device="cpu"

model = get_bert_classifier(BERT_MODEL, len(label2idx), model_file=output_model_file, device=device)
model.eval()

_, test_correct, test_predicted = evaluate(model, test_dataloader, device)

print("Test performance:", precision_recall_fscore_support(test_correct, test_predicted, average="micro"))
print(classification_report(test_correct, test_predicted, target_names=target_names))


# In[6]:


c = 0
for item, predicted, correct in zip(test_data, test_predicted, test_correct):
    assert item["label"] == idx2label[correct]
    c += (item["label"] == idx2label[predicted])
    print("{}#{}#{}".format(item["text"], idx2label[correct], idx2label[predicted]))
    
print(c)
print(c/len(test_data))

