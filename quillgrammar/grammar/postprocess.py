from typing import Dict

from .constants import Tag, GrammarError, TokenSet, POS
from .verbutils import has_noun_subject, get_subject, is_passive, has_pronoun_subject, \
    is_perfect, comma_between_subject_and_verb
from .error import Error
from .checks.myspacy import nlp


def classify_error(error: Error, config: Dict) -> Error:
    """ Subclassify or correct specific error types, such as SVA errors,
    which need a more specific type"""

    # The predicted sentence is the sentence where the grammar error has
    # been corrected. If the error does not have a predicted sentence,
    # we just take the original sentence.
    if error.predicted_sentence is not None:
        doc = nlp(error.predicted_sentence)
    else:
        doc = error.document

    # Locate the error token in the sentence.
    predicted_token = None
    for t in doc:
        if t.idx == error.index:
            predicted_token = t
    if not predicted_token:
        return error

    # Possessive pronoun errors that do not refer to a pronoun,
    # are probably plural-possessive errors

    if error.type == GrammarError.POSSESSIVE_PRONOUN.value and predicted_token.pos_ == POS.NOUN.value:
        error.set_type(GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value, config)

    # Subclassify subject-verb agreement errors and add the subject to the error
    elif error.type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
        if predicted_token.tag_ == Tag.SIMPLE_PAST_VERB.value:
            return None

        subject = get_subject(predicted_token, full=True)
        error.subject = "".join([t.text_with_ws for t in subject]).strip() if subject is not None else None
        error.subject_idx = subject[0].idx if subject is not None else None

        subject_set = set([t.text.lower() for t in subject]) if subject is not None else None

        if comma_between_subject_and_verb(subject, predicted_token, doc):
            error.set_type(GrammarError.SVA_SEPARATE.value, config)
        elif predicted_token.text.lower() in TokenSet.BE_FORMS.value and is_passive(predicted_token):
            error.set_type(GrammarError.PASSIVE_WITH_INCORRECT_BE.value, config)
        elif subject is not None and predicted_token.i < subject[0].i:
            error.set_type(GrammarError.SVA_INVERSION.value, config)
        elif subject is not None and len(subject_set.intersection(TokenSet.INDEF_PRONOUNS.value)) > 0:
            error.set_type(GrammarError.SVA_INDEFINITE.value, config)
        elif has_noun_subject(predicted_token):
            subject_token = get_subject(predicted_token, full=False)
            if subject_token.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                error.set_type(GrammarError.SVA_COLLECTIVE_NOUN.value, config)
            else:
                error.set_type(GrammarError.SVA_SIMPLE_NOUN.value, config)
        elif has_pronoun_subject(predicted_token):
            error.set_type(GrammarError.SVA_PRONOUN.value, config)
        else:
            return None

    return error
