from typing import List

from spacy.tokens.doc import Doc
from spacy.tokens.span import Span

from spacy.tokens.token import Token

from quillgrammar.grammar.constants import Dependency, Tag, POS, TokenSet, GrammarError
from quillnlp.grammar.myspacy import nlp

# Auxiliary verb functions:


def is_negated_with_contraction(token, sentence):
    if len(sentence) > token.i+1 and sentence[token.i+1].text == "n't":
        return True
    return False


def has_noun_subject(token: Token):
    subject = get_subject(token, full=True)

    if subject is not None:
        for t in subject:
            if (t.dep_ == Dependency.PASS_SUBJECT.value or t.dep_ == Dependency.SUBJECT.value) \
                    and (t.pos_ == POS.NOUN.value or t.pos_ == POS.PROPER_NOUN.value):
                return True
    return False


def has_pronoun_subject(token: Token):
    subject = get_subject(token, full=True)

    if subject is not None:
        for t in subject:
            if (t.dep_ == Dependency.PASS_SUBJECT.value or t.dep_ == Dependency.SUBJECT.value) \
                    and t.pos_ == POS.PRONOUN.value:
                return True
    return False


def subject_has_neither(verb: Token):
    subject = get_subject(verb)

    if subject is None:
        return False

    for token in subject.lefts:
        if token.text.lower() == "neither":
            return True
    return False


def subject_has_either(verb: Token, sentence: Span):
    # For some reason spaCy analyzes "either or" differently than "neither nor"
    subject = get_subject(verb)

    if subject is None:
        return False

    right_tokens = list(subject.rights)
    if len(right_tokens) > 0 and right_tokens[0].text == "or" and "either" in sentence.text.lower()[:subject.idx]:
        return True
    return False


def has_following_subject(verb: Token):
    """ Returns True if the verb's subject comes after it in the sentence,
    and false otherwise. """
    subject = get_subject(verb)
    if subject is not None and subject.idx > verb.idx:
        return True
    return False


def is_past(verb: Token) -> bool:
    """ Determines whether a verb is simple past. """
    return verb.tag_ == Tag.SIMPLE_PAST_VERB.value


def is_future(verb: Token) -> bool:
    """ Determines whether a verb is future. """
    for child in verb.lefts:
        if child.lemma_ == "will" and \
                child.dep_ == Dependency.AUX.value and \
                child.tag_ == Tag.MODAL_VERB.value:
            return True
    return False


def is_past_perfect(verb: Token) -> bool:
    """ Determines whether a verb is past perfect. """
    if not verb.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
        return False

    for child in verb.lefts:
        if child.lemma_ == "have" and \
                child.dep_ == Dependency.AUX.value and \
                child.tag_ == Tag.SIMPLE_PAST_VERB.value:
            return True
    return False


def is_present(verb: Token) -> bool:
    """ Determines if a verb form is present. """
    if is_future(verb):
        return False
    return verb.tag_ == Tag.PRESENT_OTHER_VERB.value or Tag.PRESENT_SING3_VERB.value


def get_subject(verb: Token, full=False):

    # If the verb is the root, we can look up its subject in its left children
    #if verb.dep_ == Dependency.ROOT.value:

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
                if token2.dep_ == Dependency.ATTRIBUTE.value:
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


def get_plural(verb: Token):
    """ Finds the plural form of a verb token. """
    if verb.lemma_ == "be":
        return "are"
    else:
        return verb._.inflect(Tag.INFINITIVE.value)


def is_indefinite(noun: Token):
    """ Determines if a noun token is indefinite or not. """
    return noun.left_edge.text.lower() in TokenSet.INDEF_PRONOUNS.value


def get_past_tenses(token: Token):
    """
    This fixes a few problems with pyinflect, such as the fact that it
    only returns "was" as the past tense of "were".

    Args:
        token:

    Returns:

    """

    PAST_TENSE_MAP = {"be": set(["was", "were"]),
                      "quit": set(["quit"])}

    if token.lemma_.lower() in PAST_TENSE_MAP:
        return PAST_TENSE_MAP[token.lemma_.lower()]
    else:
        past_tense = token._.inflect(Tag.SIMPLE_PAST_VERB.value)
        if past_tense is None:
            return set()
        else:
            return set([past_tense.lower()])


def has_inversion(doc):
    for token in doc:
        if token.pos_ == POS.VERB.value:
            subject = get_subject(token)
            if subject is not None and subject.i > token.i:
                return True
    return False


def token_has_inversion(token):
    if token.tag_.startswith("V"):
        subject = get_subject(token)
        if subject is not None and subject.i > token.i:
            return True
    return False

# Synthetic functions


def replace_past_simple_with_past_perfect(sentence):

    doc = nlp(sentence)
    new_sentence = ""

    for token in doc:
        if token.dep_ == Dependency.ADVERBIAL_CLAUSE.value and is_past(token) and is_past_perfect(token.head):
            new_sentence += "had "
        new_sentence += token.text_with_ws

    return new_sentence


def get_perfect_progressives(doc: Doc) -> List[Token]:
    """ Finds all perfect progressives (e.g. 'have been working')
    in a document. """
    perfect_progressives = []
    for token in doc:
        if token.tag_ == Tag.PRESENT_PARTICIPLE_VERB.value:
            have, been = 0, 0
            for token2 in token.lefts:
                if token2.lemma_ == "have":
                    have = 1
                elif token2.text == "been" and have:
                    been = 1
            if have and been:
                perfect_progressives.append(token)

    return perfect_progressives


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
    for child in verb.lefts:
        if child.dep_ == Dependency.PASS_AUXILIARY.value:
            return True
    return False