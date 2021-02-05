from quillnlp.utils import detokenize
from quillnlp.utils import extract_referents_from_xml_tagged_strings


def test_detokenization1():

    sentence_in = "This is a tokenized sentence ."
    sentence_out = "This is a tokenized sentence."

    detokenized_sentence = detokenize(sentence_in)
    assert detokenized_sentence == sentence_out


def test_detokenization2():

    sentence_in = "This ca n't and wo n't do ."
    sentence_out = "This can't and won't do."

    detokenized_sentence = detokenize(sentence_in)
    assert detokenized_sentence == sentence_out


def test_extract_referents_from_xml_tagged_strings():
    s = ("<ref id=0>Schools</ref> should not allow <ref id=1>junk food</ref> "
         "to be sold on campus but <ref id=1>it</ref> generates money for schools")
    assert (
            list(extract_referents_from_xml_tagged_strings([s]))
            == [{'text': 'Schools should not allow junk food to be sold on campus but it generates money for schools',
                 'refs': [
                     {'start': 0, 'end': 7, 'str_': 'Schools', 'id': '0'},
                     {'start': 25, 'end': 34, 'str_': 'junk food', 'id': '1'},
                     {'start': 60, 'end': 62, 'str_': 'it', 'id': '1'}]}]
    )


def test_extract_referents_from_xml_tagged_strings2():
    s = ("<ref id=0>Schools</ref> should not allow <ref id=1>junk food</ref> "
        "to be sold on campus because <ref id=0>they</ref> should provide more "
        "healthy options for students to choose")
    assert (
            list(extract_referents_from_xml_tagged_strings([s]))
            == [{'text': 'Schools should not allow junk food to be sold on campus because they should provide more healthy options for students to choose',
                 'refs': [
                     {'start': 0, 'end': 7, 'str_': 'Schools', 'id': '0'},
                     {'start': 25, 'end': 34, 'str_': 'junk food', 'id': '1'},
                     {'start': 64, 'end': 68, 'str_': 'they', 'id': '0'}]}]
    )

