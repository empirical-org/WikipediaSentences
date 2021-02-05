import os
from collections import Counter

from transformers import AlbertTokenizer, AutoModelWithLMHead, pipeline

from quillgrammar.grammar.checks.myspacy import nlp
from quillgrammar.grammar.constants import GrammarError, PRESENT_VERB_TAGS, PAST_VERB_TAGS

synonyms = {
    "am": ["'m"],
    "are": ["'re"],
    "is": ["'s"],
    "have": ["'ve"],
    "will": ["'ll", "wo"],
    "would": ["'d"],
    "had": ["'d"],
    "wo": ["will"],
    "ca": ["can"],
    "'m": ["am"],
    "'re": ["re"],
    "'s": ["is"],
    "'ve": ["have"],
    "'ll": ["will"],
    "'d": ["would", "had"],
    "can": ["ca"],
}


class BertPredictor(object):
    """Interface for constructing custom predictors."""

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.pipeline = pipeline('fill-mask', model=model, tokenizer=tokenizer, topk=100)
        self.nlp = nlp

    def correct_instance(self, instance):

        sentence = instance["sentence"]
        for target in instance["targets"]:

            token = target["token"]
            start = target["start"]
            alternative_forms = set(target["alternatives"])
            for f in target["alternatives"]:
                if f in synonyms:
                    alternative_forms.update(synonyms[f])

            masked_sentence = sentence[:start] + self.tokenizer.mask_token + sentence[start+len(token):]
            predictions = self.pipeline(masked_sentence)

            tag_counter = Counter()
            for prediction in predictions:
                predicted_token = self.pipeline.tokenizer.convert_ids_to_tokens(prediction["token"])
                predicted_token = predicted_token.replace("▁", "")  # for Albert tokenizer

                correct_sentence = masked_sentence.replace(self.pipeline.tokenizer.mask_token,
                                                           predicted_token)

                correct_doc = self.nlp(correct_sentence)
                predicted_tag = None
                for t in correct_doc:
                    if t.idx == start:
                        predicted_tag = t.tag_
                        tag_counter.update([predicted_tag])
                        break

                # A question mark error should only be flagged if the question mark is more
                # probable than a full stop, not just if it is more probable than the observed
                # punctuation sign.
                if target["error_type"] == GrammarError.QUESTION_MARK.value and predicted_token == ".":
                    break

                elif predicted_tag and predicted_tag == "VBZ" and target["tag"] == "VBZ":
                    break

                elif predicted_tag and predicted_tag == "VBP" and target["tag"] == "VBP":
                    break

                elif predicted_tag and predicted_tag == "VB" and target["tag"] == "VB":
                    break

                elif predicted_tag and predicted_tag == "VBN" and target["tag"] == "VBN":
                    break

                elif predicted_tag and predicted_tag == "VBD" and target["tag"] == "VBD":
                    break

                elif sum(tag_counter.values()) >= 10:
                    predicted_tag = tag_counter.most_common()[0][0]
                    if predicted_tag in PRESENT_VERB_TAGS and \
                            target["tag"] in PRESENT_VERB_TAGS and \
                            target["tag"] != predicted_tag:
                        return {"correct": correct_sentence,
                                "original_token": token,
                                "start": start,
                                "predicted_token": predicted_token,
                                "error_type": target["error_type"]}

                    elif predicted_tag in PAST_VERB_TAGS and \
                            target["tag"] in PAST_VERB_TAGS and \
                            target["tag"] != predicted_tag:
                        return {"correct": correct_sentence,
                                "original_token": token,
                                "start": start,
                                "predicted_token": predicted_token,
                                "error_type": target["error_type"]}


                # If the token itself is ranked highest in the list of predictions,
                # then it is likely correct.
                elif predicted_token.lower() == token.lower():
                    break

                # If a synonym of the token is ranked highest in the list of predictions,
                # then it is likely correct.
                elif token.lower() in synonyms and predicted_token in synonyms[token.lower()]:
                    break

                # If an alternative form is ranked highest in the list of predictions,
                # then the token is likely an error.
                elif predicted_token in alternative_forms:

                    return {"correct": correct_sentence,
                            "original_token": token,
                            "start": start,
                            "predicted_token": predicted_token,
                            "error_type": target["error_type"]}

        return {"correct": sentence,
                "error": None}

    def predict(self, instances, **kwargs):
        """Performs custom prediction.

        Instances are the decoded values from the request. They have already
        been deserialized from JSON.

        Args:
            instances: A list of prediction input instances.
            **kwargs: A dictionary of keyword args provided as additional
                fields on the predict request body.

        Returns:
            A list of outputs containing the prediction results. This list must
            be JSON serializable.
        """
        return [self.correct_instance(instance) for instance in instances]

    @classmethod
    def from_path(cls, model_dir):
        """Creates an instance of Predictor using the given path.

        Loading of the predictor should be done in this method.

        Args:
            model_dir: The local directory that contains the exported model
                file along with any additional files uploaded when creating the
                version resource.

        Returns:
            An instance implementing this Predictor class.
        """

        model = AutoModelWithLMHead.from_pretrained(os.path.join(model_dir, "model"))
        tokenizer = AlbertTokenizer.from_pretrained(os.path.join(model_dir, "tokenizer"))

        return cls(model, tokenizer)
