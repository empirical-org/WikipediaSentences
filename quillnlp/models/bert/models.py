import torch
from torch import nn
from transformers.modeling_bert import BertPreTrainedModel, BertModel, BertForSequenceClassification
from transformers.modeling_distilbert import DistilBertForSequenceClassification


class BertForMultiLabelSequenceClassification(BertPreTrainedModel):
    """A BERT model that has been adapted for multi-label sequence classification
    by replacing the original loss function with a BCEWithLogitsLoss.
    """
    def __init__(self, config):
        super(BertForMultiLabelSequenceClassification, self).__init__(config)
        self.num_labels = config.num_labels

        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, self.config.num_labels)
        self.init_weights()


    def forward(self, input_ids, token_type_ids=None, attention_mask=None, labels=None,
                position_ids=None, head_mask=None):
        outputs = self.bert(input_ids, position_ids=position_ids, token_type_ids=token_type_ids,
                            attention_mask=attention_mask, head_mask=head_mask)
        pooled_output = outputs[1]

        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)

        outputs = (logits,) + outputs[2:]  # add hidden states and attention if they are here

        if labels is not None:
            loss_fct = nn.BCEWithLogitsLoss()
            loss = loss_fct(logits, labels)
            outputs = (loss,) + outputs

        return outputs  # (loss), logits, (hidden_states), (attentions)


class BertForSequenceEmbeddings(BertPreTrainedModel):
    """ A BERT model that simply returns sequence embeddings for a given input. These are
    the embeddings produced for the [CLS] token at the start of the output, which
    normally serve as input for the classification model we finetune.
    """

    def __init__(self, config):
        super(BertForSequenceEmbeddings, self).__init__(config)
        self.num_labels = config.num_labels
        print("NUM", config.num_labels)

        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, self.config.num_labels)

        self.apply(self.init_weights)

    def forward(self, input_ids, token_type_ids=None, attention_mask=None,
                position_ids=None, head_mask=None):
        outputs = self.bert(input_ids, position_ids=position_ids, token_type_ids=token_type_ids,
                            attention_mask=attention_mask, head_mask=head_mask)
        pooled_output = outputs[1]

        pooled_output = self.dropout(pooled_output)

        return pooled_output


def get_bert_classifier(model_type: str, num_labels: int,
                        model_file: str=None, device: str="cpu") -> BertForSequenceClassification:
    """
    Load a BertForSequenceClassification model, either from a model file with a finetuned
    model, or as a simple pretrained model.

    Args:
        model_type: the type of BERT model to load, e.g. "bert-base-uncased"
        num_labels: the number of cells for the output layer of the classifier
        model_file: if we load a finetuned model, this is the file where the model is saved
        device: the device to load the model to ("cpu" or "cuda")

    Returns: a BertForSequenceClassification model

    """
    if model_file:
        model_state_dict = torch.load(model_file, map_location=lambda storage, loc: storage)

        if "distilbert" in model_type:
            model = DistilBertForSequenceClassification.from_pretrained(model_type,
                                                                        state_dict=model_state_dict,
                                                                        num_labels=num_labels)
        else:
            model = BertForSequenceClassification.from_pretrained(model_type, state_dict=model_state_dict,
                                                              num_labels=num_labels)
    else:
        if "distilbert" in model_type:
            model = DistilBertForSequenceClassification.from_pretrained(model_type, num_labels=num_labels)
        else:
            model = BertForSequenceClassification.from_pretrained(model_type, num_labels=num_labels)

    model.to(device)
    return model


def get_multilabel_bert_classifier(model_type: str, num_labels: int,
                        model_file: str = None, device: str = "cpu") -> BertForMultiLabelSequenceClassification:
    """
    Load a BertForMultiLabelSequenceClassification model, either from a model file with a finetuned
    model, or as a simple pretrained model.

    Args:
        model_type: the type of BERT model to load, e.g. "bert-base-uncased"
        num_labels: the number of cells for the output layer of the classifier
        model_file: if we load a finetuned model, this is the file where the model is saved
        device: the device to load the model to ("cpu" or "cuda")

    Returns: a BertForSequenceClassification model

    """
    if model_file:
        model_state_dict = torch.load(model_file, map_location=lambda storage, loc: storage)
        model = BertForMultiLabelSequenceClassification.from_pretrained(model_type,
                                                                        state_dict=model_state_dict,
                                                                        num_labels=num_labels)
    else:
        model = BertForMultiLabelSequenceClassification.from_pretrained(model_type,
                                                                        num_labels=num_labels)

    model.to(device)
    return model
