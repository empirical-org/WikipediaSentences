import re
from collections import namedtuple
from typing import List, Set

from spacy.tokens import Token, Doc
import lemminflect

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

from quillgrammar.grammar.constants import TokenSet, GrammarError, Tag, POS
from quillnlp.grammar.verbs import agreement
from quillnlp.grammar.myspacy import nlp
from quillnlp.grammar.verbutils import has_noun_subject, has_pronoun_subject, is_passive, in_have_been_construction, \
    get_past_tenses, has_inversion, get_subject, token_has_inversion

Error = namedtuple("Error", ["text", "index", "type", "subject"])

PRESENT_VERB_TAGS = set(["VBZ", "VB", "VBP"])
BE_FORMS = set(["be", "am", "are", "is"])
CONTRACTED_BE_FORMS = set(["'s", "'m", "'re"])
TARGET_TOKENS = {"then": ["than"],
                 "than": ["then"],
                 "i": ["me", "my", "mine"],
                 "you": ["your", "yours"],
                 "he": ["him", "his"],
                 "she": ["her", "hers"],
                 "it": ["its"],
                 "we": ["us", "our", "ours"],
                 "they": ["them", "their", "theirs"],
                 "me": ["i"],
                 "my": ["i"],
                 "mine": ["i"],
                 "your": ["you"],
                 "yours": ["you"],
                 "him": ["he"],
                 "his": ["he"],
                 "her": ["she"],
                 "hers": ["she"],
                 "its": ["it"],
                 "us": ["we"],
                 "our": ["we"],
                 "ours": ["we"],
                 "them": ["they"],
                 "their": ["they"],
                 "theirs": ["they"],
                 "an": ["a"],
                 "a": ["an"],
                 "man": ["men"],
                 "men": ["man"],
                 "been": ["is", "are", "was"],
                 ".": ["?"],
                 ";": ["?"],
                 ":": ["?"],
                 ",": ["?"],
                 "!": ["?"]}

TOKENS2ERRORS = {"then": GrammarError.THAN_THEN.value,
                 "than": GrammarError.THAN_THEN.value,
                 "i": GrammarError.OBJECT_PRONOUN.value,
                 "you": GrammarError.OBJECT_PRONOUN.value,
                 "he": GrammarError.OBJECT_PRONOUN.value,
                 "she": GrammarError.OBJECT_PRONOUN.value,
                 "we": GrammarError.OBJECT_PRONOUN.value,
                 "they": GrammarError.OBJECT_PRONOUN.value,
                 "me": GrammarError.SUBJECT_PRONOUN.value,
                 "my": GrammarError.SUBJECT_PRONOUN.value,
                 "mine": GrammarError.SUBJECT_PRONOUN.value,
                 "your": GrammarError.SUBJECT_PRONOUN.value,
                 "yours": GrammarError.SUBJECT_PRONOUN.value,
                 "him": GrammarError.SUBJECT_PRONOUN.value,
                 "his": GrammarError.SUBJECT_PRONOUN.value,
                 "her": GrammarError.SUBJECT_PRONOUN.value,
                 "hers": GrammarError.SUBJECT_PRONOUN.value,
                 "its": GrammarError.SUBJECT_PRONOUN.value,
                 "it": GrammarError.SUBJECT_PRONOUN.value,
                 "us": GrammarError.SUBJECT_PRONOUN.value,
                 "our": GrammarError.SUBJECT_PRONOUN.value,
                 "ours": GrammarError.SUBJECT_PRONOUN.value,
                 "them": GrammarError.SUBJECT_PRONOUN.value,
                 "their": GrammarError.SUBJECT_PRONOUN.value,
                 "theirs": GrammarError.SUBJECT_PRONOUN.value,
                 "a": GrammarError.ARTICLE.value,
                 "an": GrammarError.ARTICLE.value,
                 "been": GrammarError.PASSIVE_WITH_INCORRECT_BE.value,
                 ".": GrammarError.QUESTION_MARK.value,
                 ":": GrammarError.QUESTION_MARK.value,
                 ";": GrammarError.QUESTION_MARK.value,
                 ",": GrammarError.QUESTION_MARK.value,
                 "!": GrammarError.QUESTION_MARK.value}


synonyms = {"am": "'m", "are": "'re", "is": "'s", "have": "'ve",
            "will": "'ll", "would": "'d", "wo": "will", "ca": "can"}
synonyms_reversed = {v: k for k, v in synonyms.items()}
synonyms.update(synonyms_reversed)

TARGET_OPEN_TAG = "<target>"
TARGET_CLOSE_TAG = "</target>"


def make_request_from_sentence(sentence: str, prompt: str = ""):
    doc = nlp(sentence)
    return make_request_from_doc(doc, prompt)


def make_request_from_doc(doc: Doc, prompt: str = ""):
    request = {
        "sentence": doc.text,
        "targets": []
    }

    prompt_char_length = len(prompt)

    for token in doc:

        if token.idx < prompt_char_length:
            continue

        alternative_forms = None

        if token.text.lower() in TARGET_TOKENS:
            alternative_forms = TARGET_TOKENS.get(token.text.lower())
        elif token.text.lower() in BE_FORMS:
            alternative_forms = set([f for f in BE_FORMS if f != token.text.lower()])
            alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
        elif token.text.lower() in CONTRACTED_BE_FORMS:
            alternative_forms = set([f for f in CONTRACTED_BE_FORMS if f != token.text.lower()])
            alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
        elif token.pos_ == POS.VERB.value:
            alternative_forms = set(
                [token._.inflect(tag) for tag in PRESENT_VERB_TAGS if not tag == token.tag_])

        if alternative_forms:
            request["targets"].append({
                "token": token.text.lower(),
                "start": token.idx,
                "alternatives": list(alternative_forms),
            })

    return request


def create_masked_sentences(sentence, tokenizer):
    for match in re.finditer(f"{TARGET_OPEN_TAG}.+?{TARGET_CLOSE_TAG}", sentence):
        target_token = match.group(0).replace(TARGET_OPEN_TAG, "").replace(TARGET_CLOSE_TAG, "")
        masked_sentence = sentence[:match.start()] + tokenizer.mask_token + sentence[match.end():]
        masked_sentence = masked_sentence.replace(TARGET_OPEN_TAG, "").replace(TARGET_CLOSE_TAG, "")
        yield {"token": target_token,
               "masked_sentence": masked_sentence,
               "alternatives": TARGET_TOKENS[target_token.lower()]}



def classify_agreement_errors(token, error_type):

    if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
        return GrammarError.PERFECT_TENSE_WITH_SIMPLE_PAST.value, None

    subject = agreement.get_subject(token, full=True)
    subject_string = " ".join([t.text.lower() for t in subject]) if subject is not None else None
    if error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
        subject_set = set([t.text.lower() for t in subject]) if subject is not None else None
        if subject is not None and token.i < subject[0].i:
            error_type = GrammarError.SVA_INVERSION.value
        elif subject is not None and len(subject_set.intersection(TokenSet.INDEF_PRONOUNS.value)) > 0:
            error_type = GrammarError.SVA_INDEFINITE.value
        elif has_noun_subject(token):
            subject = agreement.get_subject(token, full=False)
            if subject.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                error_type = GrammarError.SVA_COLLECTIVE_NOUN.value
            else:
                error_type = GrammarError.SVA_SIMPLE_NOUN.value
        elif has_pronoun_subject(token):
            error_type = GrammarError.SVA_PRONOUN.value

    return error_type, subject_string


class GoogleAIModelChecker:

    def __init__(self):
        self.project = "comprehension-247816"
        self.model_name = "grammartest"
        self.version_name = "v4"

    def check(self, doc, prompt):

        request = make_request_from_doc(doc, prompt)

        # JSON format the requests
        request_data = {'instances': [request]}

        # Authenticate and call CMLE prediction API
        credentials = GoogleCredentials.get_application_default()
        api = discovery.build('ml', 'v1', credentials=credentials,
                              discoveryServiceUrl='https://storage.googleapis.com/cloud-ml/discovery/ml_v1_discovery.json')

        parent = 'projects/%s/models/%s/versions/%s' % (self.project, self.model_name, self.version_name)

        response = api.projects().predict(body=request_data, name=parent).execute()
        prediction = response["predictions"][0]

        if prediction["error"]:
            return [Error(prediction["original_token"],
                          prediction["start"],
                          prediction["error"],
                          None)]
        return None