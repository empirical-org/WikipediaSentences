import csv
import json
import os
import re
import requests
import numpy as np
import spacy
import subprocess
import tensorflow as tf
import tflearn
from nltk.util import ngrams, trigrams
from pattern.en import conjugate
from .feedback import *
from .infinitive_phrase_detect import (detect_infinitive_phrase,
        detect_missing_verb)
from .sva_classifier import get_feedback as get_subject_verb_agreement_feedback

model_name = os.environ.get('QUILL_SPACY_MODEL', 'en_core_web_lg')
if model_name != 'en_core_web_lg':
    nlp = spacy.load(model_name)
else:
    import en_core_web_lg
    nlp = en_core_web_lg.load()

# relative path resolution
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

LT_SERVER = \
        '{}/v2/check'.format(os.environ.get('LT_URI','http://localhost:8081'))
_PARTICIPLE_TRIGRAM_INDEX = os.path.join(__location__, 'data', 'participlevocabindex.csv')
_PARTICIPLE_MODEL = os.path.join(__location__, 'models', 'participle_model.tfl')

class Feedback(object):
    """Result feedback class"""
    def __init__(self):
        self.human_readable = '' # human readable advice
        self.primary_error = None
        self.specific_error = None
        self.matches = {}        # possible errors

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return self.human_readable

# Private methods

def _build_trigram_indices(trigram_index):
    """Build a dictionary of trigrams and their indices from a csv"""
    result = {}
    trigram_count = 0
    for key, val in csv.reader(open(trigram_index)):
        result[key] = int(val)
        trigram_count += 1
    return result, trigram_count

def _build_model(trigram_count):
    # This resets all parameters and variables, leave this here
    tf.reset_default_graph()

    net = tflearn.input_data([None, trigram_count])
    net = tflearn.fully_connected(net, 200, activation='ReLU')      # Hidden
    net = tflearn.fully_connected(net, 25, activation='ReLU')      # Hidden
    net = tflearn.fully_connected(net, 2, activation='softmax')   # Output
    net = tflearn.regression(net, optimizer='sgd', learning_rate=0.1, loss='categorical_crossentropy')
    model = tflearn.DNN(net)
    return model

def _textStringToPOSArray(text):
    doc = nlp(text)
    tags = []
    for word in doc:
        tags.append(word.tag_)
    return tags

def _find_ngrams(input_list, n):
    """TODO: this method appears unused. Deprecate it?"""
    return zip(*[input_list[i:] for i in range(n)])

def _getPOSTrigramsForTextString(text):
    tags = _textStringToPOSArray(text)
    tgrams = list(trigrams(tags))
    return tgrams

def _trigramsToDictKeys(trigrams):
    keys = []
    for trigram in trigrams:
        keys.append('>'.join(trigram))
    return keys

def _textToTrigrams(text):
    return _trigramsToDictKeys(_getPOSTrigramsForTextString(text))

def _text_to_vector(text,trigram2idx, trigram_count):
    wordVector = np.zeros(trigram_count)
    for word in _textToTrigrams(text):
        index = trigram2idx.get(word, None)
        if index != None:
            wordVector[index] += 1
    return wordVector

def _begins_with_one_of(sentence, parts_of_speech):
    """Return True if the sentence or fragment begins with one of the parts of
    speech in the list, else False"""
    doc = nlp(sentence)
    if doc[0].tag_ in parts_of_speech:
        return True
    return False

# Initializations

## Load fragment dectection models
prefixes = ['participle'] # => eventually, [participle, infinitive,
                          #    afterthought, lonelyverb, subordinate,
                          #    appositive, sva]
models = {}
trigram2idx = {}
trigram_count = {}
for prefix in prefixes:
    _trigram_index = os.path.join(__location__, 'data',
            '{}vocabindex.csv'.format(prefix))
    trigram2idx[prefix], trigram_count[prefix] = _build_trigram_indices(_trigram_index)
    models[prefix] = _build_model(trigram_count[prefix])
    models[prefix].load(os.path.join(__location__, 'models',
            '{}_model2.tfl'.format(prefix)))

# Public methods


def get_language_tool_feedback(sentence):
    """Get matches from languagetool"""
    payload = {'language':'en-US', 'text':sentence}
    try:
        r = requests.post(LT_SERVER, data=payload)
    except requests.exceptions.ConnectionError as e:
        raise requests.exceptions.ConnectionError('''The languagetool server is
        not running.  Try starting it with "ltserver" ''')
    if r.status_code >= 200 and r.status_code < 300:
        return r.json().get('matches', [])
    return []


def is_participle_clause_fragment(sentence):
    """Supply a sentence or fragment and recieve a confidence interval"""
    # short circuit if sentence or fragment doesn't start with a participle
    # past participles can sometimes look like adjectives -- ie, Tired
    if not _begins_with_one_of(sentence, ['VBG', 'VBN', 'JJ']):
        return 0.0

    if _begins_with_one_of(sentence, ['JJ']):
        doc = nlp(sentence)
        fw = [w for w in doc][0]
        # Beautiful toy birds
        if fw.dep_ == 'amod':
            return 0.0

    # short circuit if sentence starts with a gerund and the gerund is the
    # subject.

    if _begins_with_one_of(sentence, ['VBG']):
        doc = nlp(sentence)
        fw = [w for w in doc][0]
        # Running is fun
        if fw.dep_.endswith('subj'):
            return 0.0

        fc = [c for c in doc.noun_chunks]
        # Dancing boys can never sing
        if str(fw) in str(fc):
            return 0.0

    positive_prob = models['participle'].predict([_text_to_vector(sentence,
        trigram2idx['participle'], trigram_count['participle'])])[0][1]
    return float(positive_prob)

def has_incorrect_infinitive_form(sentence):
    """
    Returns whether the sentence has an incorrect infinitive

    For example: "To eats" or "To danced" (should be "To eat" and "To dance")
    """
    doc = nlp(sentence)
    prev_word = None
    for w in doc:
        if prev_word == 'to' and w.tag_.startswith('VB') and w.tag_ != 'VB':
            return True
        prev_word = w.text.lower()
    return False

def check(sentence):
    """Supply a sentence or fragment and recieve feedback"""

    # How we decide what to put as the human readable feedback
    #
    # Our order of prefence is,
    #
    # 1. Spelling errors.
    #   - A spelling error can change the sentence meaning
    # 2. Subject-verb agreement errors
    # 3. Subordinate conjunction starting a sentence
    # 4. Participle phrase fragment
    # 5. Other errors

    result = Feedback()
    is_missing_verb = detect_missing_verb(sentence)
    is_infinitive = detect_infinitive_phrase(sentence)
    is_participle = is_participle_clause_fragment(sentence)
    lang_tool_feedback = get_language_tool_feedback(sentence)
    is_incorrect_infinitive_form = has_incorrect_infinitive_form(sentence)
    subject_and_verb_agree = get_subject_verb_agreement_feedback(sentence)
    ####
    if is_missing_verb: # Lowest priority
        result.matches['missing_verb'] = True
        result.human_readable = MISSING_VERB_ADVICE.replace('\n', '')
        result.primary_error = 'MISSING_VERB_ERROR'
        result.specific_error = 'MISSING_VERB'
    if is_participle > .5:
        result.matches['participle_phrase'] = is_participle
        result.human_readable = PARTICIPLE_FRAGMENT_ADVICE.replace('\n', '')
        result.primary_error = 'FRAGMENT_ERROR'
        result.specific_error = 'PARTICIPLE_PHRASE'
    if lang_tool_feedback:
        result.matches['lang_tool'] = lang_tool_feedback
        for ltf in lang_tool_feedback:
            if ltf['rule']['id'] == 'SENTENCE_FRAGMENT':
                result.human_readable = lang_tool_feedback[0]['message']
                result.primary_error = 'FRAGMENT_ERROR'
                result.specific_error = 'SUBORDINATE_CLAUSE'
    if is_infinitive:
        result.matches['infinitive_phrase'] = True
        result.human_readable = INFINITIVE_PHRASE_ADVICE.replace('\n', '')
        result.primary_error = 'INFINITIVE_PHRASE_ERROR'
        result.specific_error = 'INFINITIVE_PHRASE'
    if lang_tool_feedback:
        result.matches['lang_tool'] = lang_tool_feedback
        for ltf in lang_tool_feedback:
            if ltf['rule']['id'] == 'MORFOLOGIK_RULE_EN_US':
                result.human_readable = ltf['message']
                result.primary_error = 'SPELLING_ERROR'
                result.specific_error = 'SPELLING_ERROR'
        if not result.primary_error:
            result.human_readable = ltf['message']
            result.primary_error = 'OTHER_ERROR'
            result.specific_error = ltf['rule']['id']
    if is_incorrect_infinitive_form:
        result.matches['incorrect_infinitive_form'] = is_incorrect_infinitive_form
        result.human_readable = INCORRECT_INFINITIVE_FORM_ADVICE.replace('\n', '')
        result.primary_error = 'INFINITIVE_FORM_ERROR'
        result.specific_error = 'INFINITIVE_FORM_ERROR'
    if subject_and_verb_agree: # Highest priority (spelling, other lang tool errors)
        result.matches['subject_verb_agreement'] = True
        result.human_readable = subject_and_verb_agree
        result.primary_error = 'SUBJECT_VERB_AGREEMENT_ERROR'
        result.specific_error = 'SUBJECT_VERB_AGREEMENT'

    ####
    if not result.matches:
        result.human_readable = STRONG_SENTENCE_ADVICE.replace('\n', '')

    return result
