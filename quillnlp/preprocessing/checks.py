import json
import re
from typing import List

from quillgrammar.grammar.error import Error
from quillgrammar.grammar.checks.myspacy import nlp

class SoResponseStartsWithThatCheck:

    name = "Starts with that"

    def check_from_text(self, sentence: str, prompt: str):
        response = sentence.replace(prompt, "").strip()
        if prompt.lower().strip().endswith(" so") and \
                response.lower().startswith("that"):
            return [Error(text="that", index=0,
                          error_type=self.name)]
        return []


class SentenceEndsInQuestionMarkCheck:

    name = "Ends in question mark"

    def check_from_text(self, sentence: str, prompt: str):
        if sentence.strip().endswith("?"):
            return [Error(text="?", index=len(sentence.strip())-1,
                         error_type=self.name)]
        return []


class ProfanityCheck:

    name = "Profanity"

    def __init__(self):
        with open("quillnlp/preprocessing/profanity.json") as i:
            self.profanities = json.load(i)

    def check_from_text(self, sentence: str, prompt: str):
        for word in self.profanities["words"]:
            if word.lower() in sentence.lower():
                match = re.search(r"(?<=\b)" + word + r"(?=\b)", sentence, re.IGNORECASE)
                if match:
                    return [Error(text=word, index=match.span()[0],
                                  error_type=self.name)]
        return []


class MultipleSentencesCheck:

    name = "Multiple Sentences"

    def check_from_text(self, sentence: str, prompt: str):
        sentences = list(nlp(sentence).sents)
        if len(sentences) > 1:
            return [Error(text=sentence, index=0,
                          error_type=self.name)]
        return []

    def check_from_tokens(self, tokens: List[str], prompt: str):
        all_but_last_tokens = set([t for t in tokens[:-1]])
        if "." in all_but_last_tokens:
            return [Error(text=".", index=0,
                          error_type=self.name)]
        return []


def perform_check(checker, sentence, prompt, message_if_not=""):

    if type(sentence) == str:
        feedback = checker.check_from_text(sentence, prompt)

    elif type(sentence) == list:
        feedback = checker.check_from_tokens(sentence, prompt)

    if len(feedback) > 0:
        return feedback[0].type
    return message_if_not
