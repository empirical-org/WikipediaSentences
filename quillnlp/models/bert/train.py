import os
from typing import List, Dict

import torch
import numpy as np
from tqdm import tqdm_notebook as tqdm, trange
from torch.nn import Sigmoid, Softmax
from torch.utils.data import DataLoader
from quillnlp.models.bert.models import BertForMultiLabelSequenceClassification

from transformers.optimization import AdamW, WarmupLinearSchedule
from transformers.modeling_bert import BertForSequenceClassification
from transformers.modeling_distilbert import DistilBertForSequenceClassification
from transformers.modeling_utils import PreTrainedModel


def train(model: PreTrainedModel, train_dataloader: DataLoader, dev_dataloader: DataLoader,
          batch_size: int, gradient_accumulation_steps: int, device, num_train_epochs: int=20,
          warmup_proportion: float=0.1, learning_rate: float=1e-5, patience: int=5,
          output_dir: str="/tmp/", model_file_name:str="model.bin") -> str:
    """
    Trains a BERT Model on a set of training data, tuning it on a set of development data

    Args:
        model: the model that will be trained
        train_dataloader: a DataLoader with training data
        dev_dataloader: a DataLoader with development data (for early stopping)
        batch_size: the batch size for training
        gradient_accumulation_steps: the number of steps that gradients will be accumulated
        device: the device where training will take place ("cpu" or "cuda")
        num_train_epochs: the maximum number of training epochs
        warmup_proportion: the proportion of training steps for which the learning rate will be warmed up
        learning_rate: the initial learning rate
        patience: the number of epochs after which training will stop if no improvement on the dev
                  set is observed
        output_dir: the directory where the model will be saved
        model_file_name: the filename of the model file

    Returns: the path to the trained model

    """

    def warmup_linear(x, warmup=0.002):
        if x < warmup:
            return x / warmup
        return 1.0 - x

    output_model_file = os.path.join(output_dir, model_file_name)

    num_train_steps = int(len(train_dataloader.dataset) / batch_size / gradient_accumulation_steps * num_train_epochs)
    max_grad_norm = 5

    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
        {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
        ]

    optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate, correct_bias=False)

    global_step = 0
    loss_history = []
    best_epoch = 0
    for epoch in trange(int(num_train_epochs), desc="Epoch"):

        model.train()
        tr_loss = 0
        for step, batch in enumerate(tqdm(train_dataloader, desc="Training iteration")):
            batch = tuple(t.to(device) for t in batch)
            input_ids, input_mask, segment_ids, label_ids = batch
            if type(model) == BertForSequenceClassification or type(model) == BertForMultiLabelSequenceClassification:
                outputs = model(input_ids, attention_mask=input_mask, token_type_ids=segment_ids, labels=label_ids)
            elif type(model) == DistilBertForSequenceClassification:
                outputs = model(input_ids, attention_mask=input_mask, labels=label_ids)
            loss = outputs[0]

            if gradient_accumulation_steps > 1:
                loss = loss / gradient_accumulation_steps

            loss.backward()

            tr_loss += loss.item()

            if (step + 1) % gradient_accumulation_steps == 0:
                lr_this_step = learning_rate * warmup_linear(global_step / num_train_steps, warmup_proportion)
                for param_group in optimizer.param_groups:
                    param_group['lr'] = lr_this_step
                optimizer.step()
                optimizer.zero_grad()
                global_step += 1

        dev_loss, _, _, _ = evaluate(model, dev_dataloader, device)

        print("Loss history:", loss_history)
        print("Dev loss:", dev_loss)

        if len(loss_history) == 0 or dev_loss < min(loss_history):
            model_to_save = model.module if hasattr(model, 'module') else model
            torch.save(model_to_save.state_dict(), output_model_file)
            best_epoch = epoch

        if epoch - best_epoch >= patience:
            print("No improvement on development set. Finish training.")
            break

        loss_history.append(dev_loss)

    return output_model_file


def evaluate(model: PreTrainedModel, dataloader: DataLoader, device: str) -> (int, List[int], List[int]):
    """
    Evaluates a Bert Model on a labelled data set.

    Args:
        model: the BertModel to be evaluated
        dataloader: the DataLoader with the test data
        device: the device where evaluation will take place ("cpu" or "cuda")

    Returns: a tuple with (the evaluation loss, a list with the correct labels,
            and a list with the predicted labels)

    """

    model.eval()

    eval_loss = 0
    nb_eval_steps = 0
    predicted_labels, correct_labels, probabilities = [], [], []

    for step, batch in enumerate(tqdm(dataloader, desc="Evaluation iteration")):
        batch = tuple(t.to(device) for t in batch)
        input_ids, input_mask, segment_ids, label_ids = batch

        with torch.no_grad():
            if type(model) == BertForSequenceClassification or type(model) == BertForMultiLabelSequenceClassification:
                tmp_eval_loss, logits = model(input_ids, attention_mask=input_mask,
                                              token_type_ids=segment_ids, labels=label_ids)
            elif type(model) == DistilBertForSequenceClassification:
                tmp_eval_loss, logits = model(input_ids, attention_mask=input_mask, labels=label_ids)

        if type(model) == BertForSequenceClassification or type(model) == DistilBertForSequenceClassification:
            softmax = Softmax()
            outputs = softmax(logits.to('cpu'))
            label_ids = label_ids.to('cpu').numpy()
            predicted_labels += list(np.argmax(outputs, axis=1))

        elif type(model) == BertForMultiLabelSequenceClassification:
            sig = Sigmoid()
            outputs = sig(logits).to('cpu').numpy()
            label_ids = label_ids.to('cpu').numpy()
            predicted_labels += list(outputs >= 0.5)

        correct_labels.extend(list(label_ids))
        probabilities.extend(list(outputs))

        eval_loss += tmp_eval_loss.mean().item()
        nb_eval_steps += 1

    eval_loss = eval_loss / nb_eval_steps

    correct_labels = np.array(correct_labels)
    predicted_labels = np.array(predicted_labels)

    return eval_loss, probabilities, correct_labels, predicted_labels

