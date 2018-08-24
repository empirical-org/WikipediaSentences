import spacy
import os

model_name = os.environ.get('QUILL_SPACY_MODEL', 'en_core_web_lg')
if model_name != 'en_core_web_lg':
    nlp = spacy.load(model_name)
else:
    import en_core_web_lg
    nlp = en_core_web_lg.load()


def detect_missing_verb(sentence):
    """Return True if the sentence appears to be missing a main verb"""
    # TODO: should this be relocated?
    doc = nlp(sentence)
    for w in doc:
        if w.tag_.startswith('VB') and w.dep_ == 'ROOT':
            return False # looks like there is at least 1 main verb
    return True # we scanned the whole sting and didn't see a main verb

def detect_infinitive_phrase(sentence):
    """Given a string, return true if it is an infinitive phrase fragment"""

    # eliminate sentences without to
    if not 'to' in sentence.lower():
        return False

    doc = nlp(sentence)
    prev_word = None
    for w in doc:
        # if statement will execute exactly once
        if prev_word == 'to':
            if w.dep_ == 'ROOT' and w.tag_.startswith('VB'): 
                return True # this is quite likely to be an infinitive phrase
            else:
                return False
        prev_word = w.text.lower()

