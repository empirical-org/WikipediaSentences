import os
import yaml
from flask import Flask, request

from quillgrammar.grammar.pipeline import GrammarPipeline

from spell.serving import BasePredictor

os.environ["SPACY_GRAMMAR_PATH"] = "/model/output_grammarmix_20210113/model-best"

class GrammarPredictor(BasePredictor):

    def __init__(self):
        self.model = None

    def predict(self, payload):

        return {"result": 1}


"""
class GrammarPredictor(BasePredictor):

    def __init__(self):
        config_file = "quillgrammar/grammar_config_test.yaml"
        with open(config_file) as i:
            config = yaml.load(i, Loader=yaml.FullLoader)

        self.model = GrammarPipeline(config)

    def predict(self, payload):

        sentence = payload["sentence"]
        prompt = payload["prompt"]
        errors = pipeline.check(sentence, prompt)
        if len(errors) > 0:
            errors.sort(reverse=True)
            error = errors[0]

            return {"text": error.text,
                    "type": error.type,
                    "index": error.index,
                    "model": error.model}

        return {"text": sentence,
                "type": None,
                "index": None,
                "model": None}
"""
