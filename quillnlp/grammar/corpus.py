import lemminflect
import random
from typing import List, Tuple, Set
from nltk.corpus import wordnet as wn
from difflib import get_close_matches as gcm
from spacy.tokens import Doc

from quillgrammar.grammar.constants import GrammarError

ADVERB_ADJECTIVE_MAP = {"well": "good"}

VERB_AGREEMENT_ERROR_TYPE = "VERB"
WOMAN_WOMEN_ERROR_TYPE = "WOMAN"
THEN_THAN_ERROR_TYPE = "THEN"
CHILD_CHILDREN_ERROR_TYPE = "CHILD"
IT_S_ITS_ERROR_TYPE = "ITS"
PLURAL_POSSESSIVE_ERROR_TYPE = GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value
ADV_ERROR_TYPE = "ADV"

PRESENT_BE = set(["be", "am", "are", "is"])
PAST_BE = set(["were", "was"])

# "Problem" verbs are verbs we do not change before "n't", because this
# problems with spaCy's tokenization, which sees "cansn't" or "wouldsn't"
# as one token rather than two.
# Note: can't is tokenized as ca+n't
PROBLEM_VERBS = set(["can", "would", "will", "ca"])

# TODO: there is still one problem here: changing a subject and then changing its verb may
# result in a correct sentence.
# This has now been fixed by NOT replacing these words when they are in subject position.
# Potentially this has also a good idea for NNS => NN+POS
TOKEN_REPLACEMENT_MAP = {"then": ("than", THEN_THAN_ERROR_TYPE),
                         "than": ("then", THEN_THAN_ERROR_TYPE),
                         "woman": ("women", WOMAN_WOMEN_ERROR_TYPE),
                         "women": ("woman", WOMAN_WOMEN_ERROR_TYPE),
                         "child": ("children", CHILD_CHILDREN_ERROR_TYPE),
                         "children": ("child", CHILD_CHILDREN_ERROR_TYPE),
                         "its": ("it's", IT_S_ITS_ERROR_TYPE)}

SUBJECT_DEPENDENCIES = set(["nsubj", "nsubjpass"])


def is_subject(token):
    return token.dep_ in SUBJECT_DEPENDENCIES


def has_plural_noun(doc: Doc) -> bool:
    """ Returns True if the document contains a plural noun and False otherwise. """
    for token in doc:
        if token.tag_ == "NNS" and token.text.endswith("s"):
            return True
    return False


def has_possessive_noun(doc: Doc) -> bool:
    """ Returns True if the document contains a possessive noun and False otherwise. """
    for token in doc:
        # Return true if we find an 's (POS) preceded by a noun.
        if token.i > 0 and token.tag_ == "POS" and doc[token.i-1].tag_.startswith("N"):
            return True
    return False


def has_third_person_singular_verb(doc: Doc) -> bool:
    """ Returns True if the document contains a third person present singular verb. """
    for token in doc:
        if token.tag_ == "VBZ":
            return True
    return False


def has_present_verb_non_third_person(doc: Doc) -> bool:
    """ Returns True if the document contains a non-third-person-singular present verb. """
    for token in doc:
        if token.tag_ == "VBP":
            return True
    return False


def has_modal(doc:Doc) -> bool:
    """ Returns True if the document contains a modal verb. """
    for token in doc:
        if token.tag_ == "MD":
            return True
    return False


def has_infinitive(doc: Doc) -> bool:
    """ Returns True if the document contains an infinitive verb. """
    for token in doc:
        if token.tag_ == "VB":
            return True
    return False


def contains_token(token: str, doc: Doc) -> bool:
    """ Returns True if the lowercased document contains the specified token. """
    tokens = set([t.text.lower() for t in doc])
    return token in tokens


def contains_phrase(token_list: List[str], doc: Doc) -> bool:
    """ Returns True if the lowercased document contains the specified phrase. """
    tokens = [t.text.lower() for t in doc]
    for i in range(len(tokens)-len(token_list)+1):
        if tokens[i:i+len(token_list)] == token_list:
            return True
    return False


def get_pos(doc: Doc) -> Set[str]:
    """ Returns the set of all pos_ attributes in the document. """
    return set([t.pos_ for t in doc])


def get_tag(doc: Doc) -> Set[str]:
    """ Returns a set of all tag_ attributes in the document. """
    return set([t.tag_ for t in doc])


def has_adverb(doc: Doc) -> bool:
    """ Returns True if the document contains an adverb. """
    return "ADV" in get_pos(doc)


def has_modal(doc: Doc) -> bool:
    """ Returns True if the document contains a modal verb.
    Modal verbs (will, can, should, etc.) have POS VERB and TAG MD"""
    return "MD" in get_tag(doc)


def has_aux(doc: Doc) -> bool:
    """ Returns True if the document contains an auxiliary verb other than be. """
    for token in doc:
        if token.pos_ == "AUX" and token.lemma_ != "be":
            return True
    return False


def has_do(doc: Doc) -> bool:
    """ Returns True if the document contains the verb 'do' as an auxiliary. """
    for token in doc:
        if token.pos_ == "AUX" and token.lemma_ == "do":
            return True
    return False


# Replacement functions


def replace_word(source_word: str, target_word: str, error_type: str, doc: Doc) -> Tuple[str, List[Tuple]]:
    """ Replace the source word by a target word in the document. """

    new_tokens = []
    entities = []
    for token in doc:
        if len(entities) > 0:  # we only make one correction per sentence
            new_tokens.append(token.text_with_ws)
        elif token.text.lower() == source_word:
            if token.text[0].isupper():
                new_tokens.append(target_word.title() + token.whitespace_)
            else:
                new_tokens.append(target_word + token.whitespace_)
            error_start_idx = len("".join(new_tokens))
            entities.append((error_start_idx, error_start_idx + len(target_word), error_type))
        else:
            new_tokens.append(token.text_with_ws)

    return "".join(new_tokens), entities


def get_adjective_for_adverb(adverb: str) -> str:
    """
    Get the adjective corresponding to an adverb, e.g. beautifully -> beautiful

    Args:
        adverb:

    Returns:

    """
    if adverb in ADVERB_ADJECTIVE_MAP:
        return ADVERB_ADJECTIVE_MAP[adverb]

    possible_adj = []
    for ss in wn.synsets(adverb):
        for lemmas in ss.lemmas():  # all possible lemmas
            for ps in lemmas.pertainyms():  # all possible pertainyms
                possible_adj.append(ps.name())
    close_matches = gcm(adverb, possible_adj)
    if len(close_matches) > 0:
        return close_matches[0]

    return None


def replace_bigram(source_bigram: List[str], target_word: str, error_type: str, doc) -> Tuple[str, List[Tuple]]:
    """
    Replace a bigram by a word in a document

    Args:
        source_bigram:
        target_word:
        error_type:
        doc:

    Returns:

    """
    new_tokens = []
    entities = []

    skip_token = False
    for token in doc:
        if skip_token:
            skip_token = False
        elif len(entities) > 0:  # we only make one correction per sentence
            new_tokens.append(token.text_with_ws)
        elif token.i < len(doc) - 1 and token.text.lower() == source_bigram[0] \
                and doc[token.i + 1].text.lower() == source_bigram[1]:
            if token.text[0].isupper():
                new_tokens.append(target_word.title() + doc[token.i + 1].whitespace_)
            else:
                new_tokens.append(target_word + doc[token.i + 1].whitespace_)
            error_start_idx = len("".join(new_tokens))
            entities.append((error_start_idx, error_start_idx + len(target_word), error_type))
            skip_token = True
        else:
            new_tokens.append(token.text_with_ws)
    return "".join(new_tokens), entities


def replace_adverb_by_adjective(error_type: str, doc: Doc) -> Tuple[str, List[Tuple]]:
    """ Replaces adverbs by adjectives in the provided document. """

    new_tokens = []
    entities = []
    for token in doc:
        if token.pos_ == "ADV":
            adjective = get_adjective_for_adverb(token.text.lower())
            if adjective is not None:

                # Get the right casing
                if token.text.istitle():
                    adjective = adjective.title()
                new_tokens.append(adjective + token.whitespace_)

                # If the adjective differs from the adverb, add an error.
                if adjective != token.text:
                    error_start_idx = len("".join(new_tokens))
                    entities.append((error_start_idx, error_start_idx + len(adjective), error_type))
            else:
                new_tokens.append(token.text_with_ws)
        else:
            new_tokens.append(token.text_with_ws)
    return "".join(new_tokens), entities


def replace_verb_form(source_tag: str, target_tag: str, error_type: str, doc: Doc) -> Tuple[str, List[Tuple]]:
    """
    Replaces all verb forms with the given source tag in the document by the corresponding
    form with the other tag

    Args:
        source_tag: the tag of the verbs that should be replaced, e.g. VBZ
        target_tag: the tag of the replacing form, e.g. VB
        error_type: the label of the error type
        doc: the document

    Returns:

    """
    # TODO: we need to find a better solution for verbs followed by "n't", where the
    # whitespace is not correct => He ben't do that.
    text = ""
    entities = []
    for token in doc:
        if token.tag_ == source_tag:
            if token.text.startswith("'"):
                text += " "
            if target_tag == "VB":
                new_verb_form = token.lemma_
            else:
                new_verb_form = token._.inflect(target_tag)

            if new_verb_form is None or new_verb_form == token.text:
                text += token.text_with_ws
            else:
                if token.text[0].isupper():
                    new_verb_form = new_verb_form.title()
                start_index = len(text)
                text += new_verb_form + token.whitespace_
                entities.append((start_index, start_index + len(new_verb_form), error_type))
        else:
            text += token.text_with_ws
    return text, entities


def replace(doc: Doc, error_ratio: float):

    text = ""
    entities = []
    skip_next = False
    for token in doc:
        if skip_next:
            skip_next = False
            continue

        # If the token is immediately followed by "n't" (no whitespace), skip
        # This avoids problems like wouldn't => wouldsn't, where the indices of the error
        # do not match a spaCy token
        elif token.i < len(doc)-1 and token.text.lower() in PROBLEM_VERBS and \
                (doc[token.i+1].text == "n't" or doc[token.i+1].text == "not")\
                and not token.whitespace_:
            new_token = token.text

        elif token.text in PRESENT_BE and random.random() < error_ratio:
            alternative_forms = PRESENT_BE - set([token.text.lower()])
            new_token = random.sample(alternative_forms, 1)[0]
            error_type = VERB_AGREEMENT_ERROR_TYPE
        elif token.text in PAST_BE and random.random() < error_ratio:
            alternative_forms = PAST_BE - set([token.text.lower()])
            new_token = random.sample(alternative_forms, 1)[0]
            error_type = VERB_AGREEMENT_ERROR_TYPE
        elif token.tag_ == "VBZ" and random.random() < error_ratio:
            new_token = token._.inflect("VB")
            error_type = VERB_AGREEMENT_ERROR_TYPE
        elif token.tag_ == "VBP" and random.random() < error_ratio:
            new_token = token._.inflect("VBZ")
            error_type = VERB_AGREEMENT_ERROR_TYPE
        elif token.tag_ == "VB" and random.random() < error_ratio:
            new_token = token._.inflect("VBZ")
            error_type = VERB_AGREEMENT_ERROR_TYPE
        elif token.tag_ == "MD" and random.random() < error_ratio:
            new_token = token._.inflect("VBZ")
            error_type = VERB_AGREEMENT_ERROR_TYPE
        elif token.text.lower() in TOKEN_REPLACEMENT_MAP and \
                not is_subject(token) and \
                random.random() < error_ratio:
            new_token, error_type = TOKEN_REPLACEMENT_MAP[token.text.lower()]
        elif token.pos_ == "ADV" and random.random() < error_ratio:
            new_token = get_adjective_for_adverb(token.text.lower())
            error_type = ADV_ERROR_TYPE
        elif token.tag_ == "NNS" and random.random() < error_ratio:
            new_token = token.lemma_ + "'s"
            error_type = PLURAL_POSSESSIVE_ERROR_TYPE
        elif token.i < len(doc)-1 and token.tag_ == "NN" and \
                doc[token.i+1].tag_ == "POS" and random.random() < error_ratio:
            new_token = token._.inflect("NNS")
            error_type = PLURAL_POSSESSIVE_ERROR_TYPE
            skip_next = True
        elif token.i < len(doc)-1 and token.text.lower() == "it" and \
                doc[token.i+1].text.lower() == "'s" and random.random() < error_ratio:
            new_token = "its"
            error_type = IT_S_ITS_ERROR_TYPE
            skip_next = True
        else:
            new_token = token.text

        if new_token is None or new_token == token.text:
            text += token.text_with_ws
        else:
            if token.text[0].isupper():
                new_token = new_token.title()

            # Add a space to the text if it does not end in a space.
            # This solves problems like he's => hebe
            if len(text) > 0 and not text[-1].isspace():
                text += " "

            start_index = len(text)
            if skip_next:
                text += new_token + doc[token.i+1].whitespace_
            else:
                text += new_token + token.whitespace_
            entities.append((start_index, start_index + len(new_token), error_type))

    return text, entities


def replace_its_vs_it_s(doc: Doc, error_ratio: float):

    text = ""
    entities = []
    skip_next = False
    for token in doc:
        if skip_next:
            skip_next = False
            continue

        # If the token is immediately followed by "n't" (no whitespace), skip
        # This avoids problems like wouldn't => wouldsn't, where the indices of the error
        # do not match a spaCy token
        elif token.i < len(doc)-1 and token.text.lower() in PROBLEM_VERBS and \
                (doc[token.i+1].text == "n't" or doc[token.i+1].text == "not")\
                and not token.whitespace_:
            new_token = token.text

        elif token.text.lower() == "its" and not is_subject(token) and \
                random.random() < error_ratio:
            new_token, error_type = TOKEN_REPLACEMENT_MAP[token.text.lower()]
        elif token.i < len(doc)-1 and token.text.lower() == "it" and \
                doc[token.i+1].text.lower() == "'s" and random.random() < error_ratio:
            new_token = "its"
            error_type = IT_S_ITS_ERROR_TYPE
            skip_next = True
        else:
            new_token = token.text

        if new_token is None or new_token == token.text or len(entities) > 0:
            text += token.text_with_ws
        else:
            if token.text[0].isupper():
                new_token = new_token.title()
                if new_token == "It'S":
                    new_token = "It's"

            # Add a space to the text if it does not end in a space.
            # This solves problems like he's => hebe
            if len(text) > 0 and not text[-1].isspace():
                text += " "

            start_index = len(text)

            if skip_next:
                text += new_token + doc[token.i+1].whitespace_
            else:
                text += new_token + token.whitespace_

            entities.append((start_index, start_index + len(new_token), error_type))

    return text, entities
