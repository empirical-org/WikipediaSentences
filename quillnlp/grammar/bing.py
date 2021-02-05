import re
import difflib

from quillgrammar.grammar.constants import GrammarError
from quillnlp.grammar.myspacy import nlp


START_INSERT = "<ins>"
END_INSERT = "</ins>"

START_DELETE = "<del>"
END_DELETE = "</del>"

START_REPLACE = "<rep>"
SEPARATE_REPLACE = "#"
END_REPLACE = "</rep>"


def find_token_at_index(doc, index):
    for token in doc:
        if token.idx <= index <= token.idx + len(token):
            return token


def compute_differences(sentence1, sentence2):

    sm = difflib.SequenceMatcher(None, sentence1, sentence2)

    original_doc = nlp(sentence1)
    corrected_doc = nlp(sentence2)

    output = []
    original_tokens = []
    corrected_tokens = []
    for opcode, a0, a1, b0, b1 in sm.get_opcodes():
        if opcode == 'equal':
            output.append(sm.a[a0:a1])
        elif opcode == 'insert':
            output.append(START_INSERT + sm.b[b0:b1] + END_INSERT)
            original_tokens.append(find_token_at_index(original_doc, a0))
            corrected_tokens.append(find_token_at_index(corrected_doc, b0))
        elif opcode == 'delete':
            output.append(START_DELETE + sm.a[a0:a1] + END_DELETE)
            original_tokens.append(find_token_at_index(original_doc, a0))
            corrected_tokens.append(find_token_at_index(corrected_doc, b0))
        elif opcode == 'replace':
            output.append(START_REPLACE + sm.a[a0:a1] + SEPARATE_REPLACE + sm.b[b0:b1] + END_REPLACE)
            original_tokens.append(find_token_at_index(original_doc, a0))
            corrected_tokens.append(find_token_at_index(corrected_doc, b0))
        else:
            pass
    return ''.join(output).lower(), original_tokens, corrected_tokens


def classify_correction(original_sentence: str, corrected_sentence: str):

    if original_sentence == corrected_sentence:
        return []

    #original_tokens = nlp(original_sentence)
    #corrected_tokens = nlp(corrected_sentence)

    errors = []

    differences, original_tokens, corrected_tokens = compute_differences(original_sentence, corrected_sentence)
    print(differences)
    print(original_tokens)
    print(corrected_tokens)
    for (t1, t2) in zip(original_tokens, corrected_tokens):
        if t1.text == t2.text:
            continue
        elif t1.text.lower() == t2.text.lower():
            errors.append(GrammarError.CAPITALIZATION.value)
        elif t1.text.lower() == "an" and t2.text.lower() == "a":
            errors.append(GrammarError.ARTICLE.value)
        elif t1.text.lower() == "a" and t2.text.lower() == "an":
            errors.append(GrammarError.ARTICLE.value)
        elif t1.text.lower() == "it" and t2.text.lower() == "its":
            errors.append(GrammarError.ITS_IT_S.value)
        elif t1.text.lower() == "its" and t2.text.lower() == "it":
            errors.append(GrammarError.ITS_IT_S.value)
        elif t1.text.lower() == "this" and t2.text.lower() == "that":
            errors.append(GrammarError.THIS_THAT.value)
        elif t1.text.lower() == "that" and t2.text.lower() == "this":
            errors.append(GrammarError.THIS_THAT.value)
        elif t1.text.lower() == "these" and t2.text.lower() == "those":
            errors.append(GrammarError.THESE_THOSE.value)
        elif t1.text.lower() == "those" and t2.text.lower() == "these":
            errors.append(GrammarError.THESE_THOSE.value)
        elif t1.text.lower() == "child" and t2.text.lower() == "children":
            errors.append(GrammarError.CHILD_CHILDREN.value)
        elif t1.text.lower() == "children" and t2.text.lower() == "child":
            errors.append(GrammarError.CHILD_CHILDREN.value)
        elif t1.text.lower() == "woman" and t2.text.lower() == "women":
            errors.append(GrammarError.WOMAN_WOMEN.value)
        elif t1.text.lower() == "women" and t2.text.lower() == "woman":
            errors.append(GrammarError.WOMAN_WOMEN.value)
        elif t1.text.lower() == "man" and t2.text.lower() == "men":
            errors.append(GrammarError.MAN_MEN.value)
        elif t1.text.lower() == "men" and t2.text.lower() == "man":
            errors.append(GrammarError.MAN_MEN.value)
        elif re.search("^\d+$", t1.text) and re.search("(^\d+,\d+)+$", t2.text):
            errors.append(GrammarError.COMMAS_IN_NUMBERS.value)
        elif t1.tag_.startswith("V") and t2.tag_.startswith("V") and t1.tag_ != t2.tag_:
            errors.append(GrammarError.SUBJECT_VERB_AGREEMENT.value)

    if "<del> </del>" in differences or "<ins> </ins>" in differences:
        errors.append(GrammarError.SPACING.value)

    return errors