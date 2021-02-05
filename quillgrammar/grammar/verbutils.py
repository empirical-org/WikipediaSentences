from typing import List

from spacy.tokens.doc import Doc
from spacy.tokens.span import Span

from spacy.tokens.token import Token

from .constants import Dependency, Tag, POS, TokenSet

# Auxiliary verb functions:


def has_noun_subject(token: Token) -> bool:
    """ Determine if the token has a noun as subject """
    subject = get_subject(token, full=True)

    if subject is not None:
        for t in subject:
            if (t.dep_ == Dependency.PASS_SUBJECT.value or t.dep_ == Dependency.SUBJECT.value) \
                    and (t.pos_ == POS.NOUN.value or t.pos_ == POS.PROPER_NOUN.value):
                return True
    return False


def has_pronoun_subject(token: Token) -> bool:
    """ Determine if the token has a pronoun subject """
    subject = get_subject(token, full=True)

    if subject is not None:
        for t in subject:
            if (t.dep_ == Dependency.PASS_SUBJECT.value or t.dep_ == Dependency.SUBJECT.value) \
                    and t.pos_ == POS.PRONOUN.value:
                return True
    return False


def get_subject(verb: Token, full=False):
    """ Get the subject of a token. If full==False, only get the word that is labelled
    with the subject dependency. If full==True, get the full subject phrase."""

    # If the verb is the root, we can look up its subject in its left children
    # if verb.dep_ == Dependency.ROOT.value:

    for token in list(reversed(list(verb.lefts))) + list(verb.rights):
        if token.dep_ == Dependency.SUBJECT.value or \
                token.dep_ == Dependency.PASS_SUBJECT.value or \
                (verb.dep_ == Dependency.CCOMP.value and token.dep_ == Dependency.ATTRIBUTE.value):
            if full:
                return list(token.lefts) + [token]
            else:
                return token

        # cases like "There is a man in the room."
        elif token.dep_ == Dependency.EXPLETIVE.value or token.dep_ == Dependency.CLAUSAL_SUBJECT.value:
            for token2 in list(reversed(list(verb.lefts))) + list(verb.rights):
                if token2.dep_ == Dependency.ATTRIBUTE.value or \
                        token2.dep_ == Dependency.DIRECT_OBJECT.value:
                    if full:
                        return list(token2.lefts) + [token2]
                    else:
                        return token2

    # If we still haven't found anything, we return the attribute
    for token in list(reversed(list(verb.lefts))) + list(verb.rights):
        if token.dep_ == Dependency.ATTRIBUTE.value:
            if full:
                return list(token.lefts) + [token]
            else:
                return token

    # otherwise we have to look up the subject of its head.
    if verb.dep_ == Dependency.AUX.value or \
            verb.dep_ == Dependency.PASS_AUXILIARY.value or \
            verb.dep_ == Dependency.CONJUNCTION.value:
        return get_subject(verb.head, full=full)

    return None


def get_past_tenses(token: Token):
    """ This fixes a few problems with pyinflect, such as the fact that it
    only returns "was" as the past tense of "were"."""

    PAST_TENSE_MAP = {"be": set(["was", "were"]),
                      "quit": set(["quit"]),
                      "have": set(["'d", "had"])}

    if token.lemma_.lower() in PAST_TENSE_MAP:
        return PAST_TENSE_MAP[token.lemma_.lower()]
    else:
        past_tense = token._.inflect(Tag.SIMPLE_PAST_VERB.value)
        if past_tense is None:
            return set()
        else:
            return set([past_tense.lower()])


def has_inversion(doc: Doc):
    """ Determine if a sentence has inversion. """
    for token in doc:
        if token.pos_ == POS.VERB.value:
            subject = get_subject(token)
            if subject is not None and subject.i > token.i:
                return True

        elif token.pos_ == POS.AUX.value and token.lemma_ == "do":
            return True

    return False


def in_have_been_construction(token: Token) -> bool:
    """ Determines whether the token is in a 'have been' construction,
    such as 'has been found'.
    """
    have, been = 0, 0
    for token2 in token.lefts:
        if token2.lemma_ == "have":
            have = 1
        elif token2.text == "been" and have:
            been = 1
    if have and been:
        return True
    return False


def is_perfect(token: Token) -> bool:
    """ Determines whether the token is in a 'have' construction.
    """
    for token2 in token.lefts:
        if token2.lemma_ == "have":
            return True
    return False


def is_passive(verb: Token) -> bool:
    """ Determines whether a verb token is passive. """

    if verb.dep_ == Dependency.PASS_AUXILIARY.value:
        return True

    for child in verb.lefts:
        if child.dep_ == Dependency.PASS_AUXILIARY.value:
            return True
    return False


def comma_between_subject_and_verb(subject, predicted_token, doc):
    """ Find out if there is a comma between subject and verb. """
    if subject is None:
        return False

    last_subject_index = subject[-1].i
    for token in doc[last_subject_index + 1:predicted_token.i]:
        if token.text == ",":
            return True
    return False
