import os
import spacy
from spacy.tokens.doc import Doc

from ..constants import GrammarError
from ..error import Error
from ..verbutils import is_passive

nlp = spacy.load("en_core_web_trf")


def replace(label):
    label = label.replace("_", " ")

    if label == "ITS":
        return GrammarError.ITS_IT_S.value
    elif label == "PLUPOS":
        return GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value
    return label


class SpaCyGrammarChecker:

    def __init__(self, spacy_path, config={}):

        self.nlp_grammar = spacy.load(spacy_path)

        # SpaCy's grammar labels are the NER labels that are not in allcaps
        self.candidate_checks = set([label for label in self.nlp_grammar.get_pipe("ner").labels if label != label.upper()])
        self.candidate_checks = set([replace(label) for label in self.nlp_grammar.get_pipe("ner").labels])
        self.candidate_checks.add(GrammarError.THEIR_THEIR_OPTIMAL.value)
        self.candidate_checks.add(GrammarError.THEIR_THEYRE_OPTIMAL.value)
        self.candidate_checks.add(GrammarError.THEIR_THERE_OPTIMAL.value)

        self.unclassified = False
        self.name = "spaCy"
        self.config = config

        self.error_types = set()
        for error in config.get("errors", []):
            if config["errors"][error] > 0:
                if error in self.candidate_checks:
                    self.error_types.add(error)
                elif error.startswith(GrammarError.SUBJECT_VERB_AGREEMENT.value):
                    self.error_types.add(GrammarError.SUBJECT_VERB_AGREEMENT.value)

        print("Initialized spaCy-based Error Check for these errors:")
        for error_check in self.candidate_checks:
            if error_check in self.error_types:
                print(f"[x] {error_check}")
            else:
                print(f"[ ] {error_check}")

    def check(self, doc: Doc, prompt=""):

        grammardoc = self.nlp_grammar(doc.text)
        errors = []
        for entity in grammardoc.ents:
            if not self.config or replace(entity.label_) in self.error_types:

                error_type = replace(entity.label_)
                if error_type == GrammarError.PERFECT_WITHOUT_HAVE.value and is_passive(entity[0]):
                    error_type = GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value

                error = Error(text=entity.text,
                              index=entity.start_char,
                              error_type=error_type,
                              model=self.name,
                              document=doc)

                errors.append(error)

        return errors
