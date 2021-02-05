import random

from spacy.tokens.token import Token

from quillgrammar.grammar.constants import GrammarError, Dependency
from quillnlp.grammar.myspacy import nlp

Token.set_extension("replace", default=None)


class ErrorGenerator:

    def generate_from_doc(self, doc):
        pass

    def generate_from_text(self, text: str):
        return self.generate_from_doc(nlp(text))


class TokenReplacementErrorGenerator(ErrorGenerator):

    def __init__(self, replacement_map, error_name):
        self.replacement_map = replacement_map
        self.name = error_name

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.lower() in self.replacement_map:
                replacement_token = self.replacement_map[token.text.lower()]

                # If the token is allcaps, the replacement token should be allcaps
                if token.text.upper() == token.text:
                    replacement_token = replacement_token.upper()

                # If the token is capitalized, the replacement token should be capitalized
                elif token.text[0].upper() == token.text[0]:
                    replacement_token = replacement_token[0].upper() + replacement_token[1:]
                new_sentence += replacement_token + token.whitespace_
                entities.append((token.idx, token.idx+len(replacement_token), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


subject_pronoun_unigram_replacements = {
    "i": ["me", "my", "mine", "my's"],
    "you": ["your", "yours", "your's"],
    "he": ["him", "his"],
    "she": ["her", "hers", "her's"],
    "we": ["us", "our",	"ours", "our's"],
    "they":	["them", "their", "their's"]
}

subject_pronoun_bigram_replacements = {
    "you're": ["your", "your's", "yours"],
    "they're": ["their", "their's", "theirs"]
}

object_pronoun_unigram_replacements = {
    "me": ["I", "I", "I", "I", "I's", "me's"],
    "him": ["he", "he", "he", "he", "he's", "him's"],
    "her": ["she", "she", "she", "she", "she's", "her's"],
    "us": ["we", "we", "we", "we", "us's"]
}

possessive_pronoun_unigram_replacements = {
    "my":	["I's", "me's", "mine", "I", "my's"],
    "your":	["you's", "yours", "you", "yous", "your's", "you're"],
    "his": ["he's",	"him's", "he", "his's"],
    "her":	["she's", "her's", "hers", "she", "shes"],
    "our":	["we's", "us's", "ours", "we", "wes", "our's"],
    "their": ["they's", "them's", "theirs", "they", "theys", "their's", "they're"],
    "mine":	["I's", "me's", "mine", "I", "my's", "my"],
    "yours": ["you's", "yours", "you", "yous", "your's", "you're", "your"],
    "hers":	["she's", "her's", "hers", "she", "shes", "her"],
    "ours":	["we's", "us's", "ours", "we", "wes", "our's", "our"],
    "theirs": ["they's", "them's", "theirs", "they", "theys", "their's", "they're", "their"]
}


class PronounReplacementErrorGenerator(ErrorGenerator):

    def __init__(self, unigram_replacement_map,
                 bigram_replacement_map,
                 dependency_test, pos, error_name):
        self.pos = pos
        self.dependency_test = dependency_test
        self.unigram_replacement_map = unigram_replacement_map
        self.bigram_replacement_map = bigram_replacement_map
        self.name = error_name

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        skip_token = False
        for i, token in enumerate(doc):
            if skip_token:
                skip_token = False
                continue

            elif len(entities) > 0:
                new_sentence += token.text_with_ws

            # Bigram replacement comes first
            elif len(doc) > i + 1 and token.text_with_ws.lower() + doc[
                    i + 1].text.lower() in self.bigram_replacement_map:

                combined_token = token.text_with_ws.lower() + doc[i + 1].text.lower()
                replacement_token = random.choice(self.bigram_replacement_map[combined_token])

                # If the token is allcaps, the replacement token should be allcaps
                if token.text.upper() == token.text:
                    replacement_token = replacement_token.upper()

                # If the token is capitalized, the replacement token should be capitalized
                elif token.text[0].upper() == token.text[0]:
                    replacement_token = replacement_token[0].upper() + replacement_token[1:]
                new_sentence += replacement_token + doc[i + 1].whitespace_
                entities.append((token.idx, token.idx + len(replacement_token), self.name))
                skip_token = True

            elif token.text.lower() in self.unigram_replacement_map and \
                    (token.text.lower() not in self.pos or
                     token.tag_ == self.pos[token.text.lower()]) and \
                    self.dependency_test(token.dep_):
                replacement_token = random.choice(self.unigram_replacement_map[token.text.lower()])

                # If the token is allcaps, the replacement token should be allcaps
                if len(token) > 1 and token.text.upper() == token.text:
                    replacement_token = replacement_token.upper()

                # If the token is capitalized, the replacement token should be capitalized
                elif token.text[0].upper() == token.text[0]:
                    replacement_token = replacement_token[0].upper() + replacement_token[1:]

                # If the token is "I" and it is not at the beginning of the sentence,
                # the replacement token should be lowercased, unless it also starts with I
                if i > 0 and token.text.startswith("I") and not replacement_token.startswith("I"):
                    replacement_token = replacement_token.lower()

                new_sentence += replacement_token + token.whitespace_
                entities.append((token.idx, token.idx+len(replacement_token), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


subject_pronoun_error_generator = PronounReplacementErrorGenerator(
    subject_pronoun_unigram_replacements,
    subject_pronoun_bigram_replacements,
    lambda x: x in set([Dependency.SUBJECT.value, Dependency.PASS_SUBJECT.value, Dependency.CLAUSAL_SUBJECT.value]),
    {},
    GrammarError.SUBJECT_PRONOUN.value
)

object_pronoun_error_generator = PronounReplacementErrorGenerator(
    object_pronoun_unigram_replacements,
    {},  # no bigram replacement for object pronouns
    lambda x: x not in set([Dependency.SUBJECT.value, Dependency.PASS_SUBJECT.value, Dependency.CLAUSAL_SUBJECT.value]),
    {"her": "PRP"},  # only replace "her" when it has a PRP tag (I see her)
    GrammarError.OBJECT_PRONOUN.value
)

possessive_pronoun_error_generator = PronounReplacementErrorGenerator(
    possessive_pronoun_unigram_replacements,
    {},  # no bigram replacement for object pronouns
    lambda x: True,
    {"her": "PRP$"},  # only replace "her" when it has a PRP$ tag (I see her car),
    GrammarError.POSSESSIVE_PRONOUN.value
)


class PluralPossessiveErrorGenerator(ErrorGenerator):

    name = GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value

    def generate_from_doc(self, doc):

        PROBLEM_VERBS = set(["can", "would", "will", "ca"])

        text = ""
        entities = []
        skip_next = False
        for token in doc:
            if skip_next:
                skip_next = False
                continue

            elif len(entities) > 0:
                text += token.text_with_ws
                continue

            # If the token is immediately followed by "n't" (no whitespace), skip
            # This avoids problems like wouldn't => wouldsn't, where the indices of the error
            # do not match a spaCy token
            elif token.i < len(doc) - 1 and token.text.lower() in PROBLEM_VERBS and \
                    (doc[token.i + 1].text == "n't" or doc[token.i + 1].text == "not") \
                    and not token.whitespace_:
                new_token = token.text

            elif token.tag_ == "NNS":
                new_token = token.lemma_ + "'s"
                error_type = self.name
            elif token.i < len(doc) - 1 and token.tag_.startswith("NN") and \
                    doc[token.i + 1].tag_ == "POS":
                new_token = token._.inflect("NNS")
                if not new_token:
                    new_token = token.lemma_ + "s"  # handle cases like Ronaldo's
                error_type = self.name
                skip_next = True
            else:
                new_token = token.text

            if new_token is None or new_token == token.text or len(entities) > 0:
                text += token.text_with_ws
                skip_next = False
            else:
                if token.text[0].isupper():
                    new_token = new_token[0].upper() + new_token[1:]

                # Add a space to the text if it does not end in a space.
                # This solves problems like he's => hebe
                if len(text) > 0 and not text[-1].isspace():
                    text += " "

                # The start index is the length of the text before
                # the new token is added
                start_index = len(text)

                # When replacing a possessive by a plural, we have to skip the next
                # token in the text ('s) and just add the whitespace that follows it.
                if skip_next:
                    text += new_token + doc[token.i + 1].whitespace_
                else:
                    text += new_token + token.whitespace_

                entities.append((start_index, start_index + len(new_token), error_type))

        return text, entities


