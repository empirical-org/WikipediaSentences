from quillnlp.grammar.bing import classify_correction
from quillgrammar.grammar.constants import GrammarError


def test_none():
    original_sentence = "This is a sentence."
    corrected_sentence = "This is a sentence."

    assert classify_correction(original_sentence, corrected_sentence) == []


def test_capitalization():
    s1 = "My name is yves."
    s2 = "My name is Yves."

    assert classify_correction(s1, s2) == [GrammarError.CAPITALIZATION.value]


def test_articles_an_a():
    s1 = "I have an cat."
    s2 = "I have a cat."

    assert classify_correction(s1, s2) == [GrammarError.ARTICLE.value]


def test_articles_a_an():
    s1 = "I have a anteater."
    s2 = "I have an anteater."

    assert classify_correction(s1, s2) == [GrammarError.ARTICLE.value]


def test_spacing1():
    s1 = "Hello , my friend."
    s2 = "Hello, my friend."

    assert classify_correction(s1, s2) == [GrammarError.SPACING.value]


def test_spacing2():
    s1 = "He is veryf riendly."
    s2 = "He is very friendly."

    assert classify_correction(s1, s2) == [GrammarError.SPACING.value]


def test_its1():
    s1 = "Its a cat."
    s2 = "It's a cat."

    assert classify_correction(s1, s2) == [GrammarError.ITS_IT_S.value]


def test_its2():
    s1 = "The cat ate it's food."
    s2 = "The cat ate its food."

    assert classify_correction(s1, s2) == [GrammarError.ITS_IT_S.value]


def test_this_that():
    s1 = "This table over there."
    s2 = "That table over there."

    assert classify_correction(s1, s2) == [GrammarError.THIS_THAT.value]


def test_that_this():
    s1 = "That table over here."
    s2 = "This table over here."

    assert classify_correction(s1, s2) == [GrammarError.THIS_THAT.value]


def test_these_those():
    s1 = "These tables over there."
    s2 = "Those tables over there."

    assert classify_correction(s1, s2) == [GrammarError.THESE_THOSE.value]


def test_those_these():
    s1 = "Those tables over here."
    s2 = "These tables over here."

    assert classify_correction(s1, s2) == [GrammarError.THESE_THOSE.value]


def test_child_children():
    s1 = "They have three child."
    s2 = "They have three children."

    assert classify_correction(s1, s2) == [GrammarError.CHILD_CHILDREN.value]


def test_children_child():
    s1 = "They have a children."
    s2 = "They have a child."

    assert classify_correction(s1, s2) == [GrammarError.CHILD_CHILDREN.value]


def test_man_men():
    s1 = "There is a men."
    s2 = "There is a man."

    assert classify_correction(s1, s2) == [GrammarError.MAN_MEN.value]


def test_men_man():
    s1 = "There are three man."
    s2 = "There are three men."

    assert classify_correction(s1, s2) == [GrammarError.MAN_MEN.value]


def test_woman_women():
    s1 = "There is a women."
    s2 = "There is a woman."

    assert classify_correction(s1, s2) == [GrammarError.WOMAN_WOMEN.value]


def test_women_woman():
    s1 = "There are three woman."
    s2 = "There are three women."

    assert classify_correction(s1, s2) == [GrammarError.WOMAN_WOMEN.value]


def test_commas_in_numbers():
    s1 = "It is 3000 miles long."
    s2 = "It is 3,000 miles long."

    assert classify_correction(s1, s2) == [GrammarError.COMMAS_IN_NUMBERS.value]


def test_not_commas_in_numbers():
    s1 = "Yes it is possible."
    s2 = "Yes, it is possible."

    assert classify_correction(s1, s2) != [GrammarError.COMMAS_IN_NUMBERS.value]


def test_subject_verb_agreement():
    s1 = "He come home."
    s2 = "He comes home."

    assert classify_correction(s1, s2) == [GrammarError.SUBJECT_VERB_AGREEMENT.value]


def test_several_errors():
    s1 = "he come home."
    s2 = "He comes home."

    assert classify_correction(s1, s2) == [GrammarError.CAPITALIZATION.value,
                                           GrammarError.SUBJECT_VERB_AGREEMENT.value]


def test_spelling_error():
    s1 = "He commes home."
    s2 = "He comes home."

    assert classify_correction(s1, s2) == []
