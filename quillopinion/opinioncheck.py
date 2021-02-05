import yaml
import spacy

from collections import namedtuple
from spacy.tokens import Doc

from quillgrammar.grammar.constants import Tag, Dependency, POS

nlp = spacy.load("en_core_web_sm")

Opinion = namedtuple("Opinion", ["type", "start", "end", "match", "precedence"])


class KeywordCheck:

    def __init__(self, config):
        self.config = config
        self.nlp = nlp
        self.checks = [
            "First-Person Opinionated Phrase Keyword Check",
            "First-Person Reference Keyword Check",
            "Second-Person Reference Keyword Check",
            "Common Opinionated Phrases Keyword Check",
            "Using Maybe",
            "Using Perhaps",
            "Using Please"
        ]

        self.checks_with_tokens = []
        for check in self.checks:
            tokenized_phrases_for_check = []
            phrases = self.config[check]
            for phrase in phrases:
                tokens = tuple([t.text.lower() for t in self.nlp(phrase)])
                tokenized_phrases_for_check.append(tokens)

            self.checks_with_tokens.append((check, tokenized_phrases_for_check))

    def check_from_text(self, sentence: str, prompt: str):
        response = sentence[len(prompt):]
        number_of_spaces = len(response) - len(response.strip())
        doc = self.nlp(response.strip())
        return self.check_from_doc(sentence, prompt, doc, number_of_spaces)

    def check_from_doc(self, sentence: str, prompt: str, doc: Doc, number_of_spaces: int):
        def lowercase(token: str) -> str:
            if token == "US":
                return token
            else:
                return token.lower()

        # Get all possible ngrams from the sentence, together with their
        # start and end index
        ngrams = {}
        for length in range(1, len(doc) + 1):
            for start in range(0, len(doc) + 1 - length):
                ngram = doc[start:start+length]
                ngram_strings = [lowercase(token.text) for token in ngram]
                ngram_start = ngram[0].idx
                ngram_end = ngram[-1].idx + len(ngram[-1])
                ngrams[tuple(ngram_strings)] = (ngram_start, ngram_end)

        # Check if any of the opinionated phrases is among the ngrams
        feedback = []
        for check_name, tokenized_phrases in self.checks_with_tokens:
            for tokenized_phrase in tokenized_phrases:
                if tokenized_phrase in ngrams:
                    start_idx = len(prompt)+number_of_spaces+ngrams[tokenized_phrase][0]
                    end_idx = len(prompt)+number_of_spaces+ngrams[tokenized_phrase][1]

                    # if the phrase starts with an apostrophe or n't, we also
                    # need to include the word before it
                    phrase = sentence[start_idx:end_idx]
                    if phrase.startswith("'") or phrase.startswith("n't"):
                        for token in doc:
                            if token.idx + len(token) == start_idx:
                                start_idx = token.idx
                                break

                    precedence = self.config["precedence"][check_name]

                    feedback.append(Opinion(check_name, start_idx, end_idx,
                                    sentence[start_idx:end_idx], precedence))

        return feedback


class ModalCheck:

    def __init__(self, config):
        self.name = "Modal Check"
        self.config = config
        self.checks = [
            "Using Should",
            "Using Must",
            "Using Need",
            "Using Ought"
        ]

        self.modals = {}
        for check in self.checks:
            self.modals[config[check][0]] = check

        self.nlp = nlp
        self.exceptions = set(["according"])

    def check_from_text(self, sentence: str, prompt: str):
        response = sentence[len(prompt):]
        number_of_spaces = len(response) - len(response.strip())
        doc = self.nlp(response.strip())
        return self.check_from_doc(sentence, prompt, doc, number_of_spaces)

    def check_from_doc(self, sentence: str, prompt: str, doc: Doc, number_of_spaces: int):
        prompt_length = len(prompt)+number_of_spaces

        feedback = []
        for token in doc:

            if token.text.lower() in self.exceptions:
                return None
            elif token.lemma_.lower() in self.modals:

                if token.tag_ == "VBD":
                    continue

                # if "ought" and "need" are "ROOT", they express an opinion
                elif token.dep_ == "ROOT":
                    start_idx = prompt_length+token.idx
                    end_idx = prompt_length+token.idx+len(token)

                    check_name = self.modals.get(token.lemma_.lower())

                    precedence = self.config["precedence"][check_name]
                    feedback.append(Opinion(check_name, start_idx, end_idx,
                                    sentence[start_idx:end_idx], precedence))

                # if "should" and "must" are "aux" and their head is "ROOT",
                # they express an opinion
                elif token.dep_ == Dependency.AUX.value and token.head.dep_ == Dependency.ROOT.value:
                    start_idx = prompt_length+token.idx
                    end_idx = prompt_length+token.idx+len(token)

                    check_name = self.modals.get(token.lemma_.lower())

                    precedence = self.config["precedence"][check_name]
                    feedback.append(Opinion(check_name, start_idx, end_idx,
                                            sentence[start_idx:end_idx], precedence))

        return feedback


class CommandCheck:

    def __init__(self, config):
        self.name = "Command Check"
        self.config = config
        self.modals = set(["should", "would", "ought", "must"])
        self.nlp = nlp
        self.exceptions = set()
        self.precedence = self.config["precedence"][self.name]

    def check_from_text(self, sentence: str, prompt: str):
        response = sentence[len(prompt):]
        number_of_spaces = len(response) - len(response.strip())
        doc = self.nlp(response.strip())
        return self.check_from_doc(sentence, prompt, doc, number_of_spaces)

    def check_from_doc(self, sentence: str, prompt: str, doc: Doc, number_of_spaces: int):

        feedback = []
        # Only identify commands in so responses
        if not prompt.strip().endswith(" so"):
            return []

        initial_token = doc[0]
        if initial_token is not None:
            if (initial_token.tag_ == Tag.INFINITIVE.value or
                initial_token.tag_ == Tag.PRESENT_OTHER_VERB.value) \
                    and initial_token.text.lower() not in self.modals:
                start_idx = len(prompt) + number_of_spaces + initial_token.idx
                end_idx = start_idx + len(initial_token)

                feedback.append(Opinion(self.name, start_idx,
                                end_idx, initial_token.text, self.precedence))

        return feedback


class StartsWithVerbCheck:
    """
    Identifies cases where the response starts with a verb. In these situations,
    we'd like to ask the student to add a subject.
    """

    def __init__(self, config):
        self.name = "Starts with Verb Check"
        self.config = config
        self.nlp = nlp
        self.exceptions = set()
        self.precedence = self.config["precedence"][self.name]

    def check_from_text(self, sentence: str, prompt: str):
        response = sentence[len(prompt):]
        number_of_spaces = len(response) - len(response.strip())
        doc = self.nlp(response.strip())
        return self.check_from_doc(sentence, prompt, doc, number_of_spaces)

    def check_from_doc(self, sentence: str, prompt: str, doc: Doc, number_of_spaces: int):

        feedback = []

        prompt_length = len(prompt.strip())
        if prompt_length == 0:
            return feedback

        for token in doc:

            # spaCy gives incorrect instances of 'its' and 'it' the VBZ tag.
            # These should not count as verbs.
            if token.text.lower() == "its" or token.text.lower() == "it":
                break

            # If the first token is a modal followed by an infinitive,
            # the sentence is an opinion. If it is a modal not followed by an infinitive,
            # this is probably a question or dependent clause and should
            # be ignored (because it wouldn't help to ask the student to
            # include an infinitive.
            if token.tag_ == Tag.MODAL_VERB.value:
                next_token = doc[token.i + 1] if len(doc) > token.i + 1 else None
                if next_token is not None and next_token.tag_ == Tag.INFINITIVE.value:
                    start_idx = len(prompt) + number_of_spaces + token.idx
                    end_idx = start_idx + len(token)

                    feedback.append(Opinion(self.name, start_idx,
                                            end_idx, token.text, self.precedence))

            # In all other cases where we the first token is a verb or an auxiliary,
            # the sentence is an opinion.
            elif (token.pos_ == POS.VERB.value or token.pos_ == POS.AUX.value) \
                    and not (token.tag_ == Tag.PRESENT_PARTICIPLE_VERB.value or
                             token.tag_ == Tag.PAST_PARTICIPLE_VERB.value):
                start_idx = len(prompt) + number_of_spaces + token.idx
                end_idx = start_idx + len(token)
                feedback.append(Opinion(self.name, start_idx,
                                        end_idx, token.text, self.precedence))
            break

        return feedback


class OpinionCheck:

    def __init__(self):
        with open("quillopinion/opinion.yaml") as i:
            config = yaml.load(i, Loader=yaml.FullLoader)

        self.checks = [
            StartsWithVerbCheck(config),
            KeywordCheck(config),
            ModalCheck(config),
            CommandCheck(config)
        ]
        self.nlp = nlp

    def check_from_text(self, sentence: str, prompt: str):

        response = sentence[len(prompt):]
        number_of_spaces = len(response) - len(response.strip())
        doc = self.nlp(response.strip())

        all_feedback = []
        for check in self.checks:
            feedback = check.check_from_doc(sentence, prompt, doc, number_of_spaces)
            if feedback is not None:
                all_feedback.extend(feedback)

        all_feedback.sort(key=lambda x: -x.precedence)

        return all_feedback

