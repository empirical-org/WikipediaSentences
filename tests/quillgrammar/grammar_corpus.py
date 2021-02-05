from quillnlp.grammar import corpus
from quillnlp.grammar.myspacy import nlp


def test_VBZ_VB_replacement():
    sentence = "He goes home."
    doc = nlp(sentence)
    text, entities = corpus.replace_verb_form("VBZ", "VB", "VERB", doc)

    assert text == "He go home."
    assert entities == [(3, 5, "VERB")]


def test_VBP_VBZ_replacement():
    sentence = "We go home."
    doc = nlp(sentence)
    text, entities = corpus.replace_verb_form("VBP", "VBZ", "VERB", doc)

    assert text == "We goes home."
    assert entities == [(3, 7, "VERB")]


def test_VBP_VB_replacement():
    """ If the two verb forms happen to be the same, the list of errors should be empty."""
    sentence = "We go home."
    doc = nlp(sentence)
    text, entities = corpus.replace_verb_form("VBP", "VB", "VERB", doc)

    assert text == "We go home."
    assert entities == []


def test_ADV_replacement1():
    sentence = "She sings beautifully."
    doc = nlp(sentence)
    text, entities = corpus.replace_adverb_by_adjective("ADV", doc)

    assert text == "She sings beautiful."


def test_ADV_replacement2():
    sentence = "Beautifully put."
    doc = nlp(sentence)
    text, entities = corpus.replace_adverb_by_adjective("ADV", doc)

    assert text == "Beautiful put."


def test_find_phrase1():
    sentence = "It's great."
    doc = nlp(sentence)
    assert corpus.contains_phrase(["it", "'s"], doc) is True


def test_find_phrase2():
    sentence = "Of course it's great."
    doc = nlp(sentence)
    assert corpus.contains_phrase(["it", "'s"], doc) is True


def test_find_phrase3():
    sentence = "Of course it's"
    doc = nlp(sentence)
    assert corpus.contains_phrase(["it", "'s"], doc) is True


def test_find_phrase4():
    sentence = "Of course it is"
    doc = nlp(sentence)
    assert corpus.contains_phrase(["it", "'s"], doc) is False
