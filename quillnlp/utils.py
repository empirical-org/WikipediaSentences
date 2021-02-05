import re

from typing import List, Generator, Dict

from quillnlp.grammar.myspacy import nlp


def detokenize(text: str) -> str:
    """
    Detokenize a text by removing spaces before punctuation. This is
    a very simple detokenization function that will sometimes fail, but
    will usually give good results.

    Args:
        text: the text to be detokenized

    Returns: the detokenized text

    """
    text = re.sub("\s+([;:,\.\?!])", "\\1", text)
    text = re.sub("\s+(n't)", "\\1", text)
    text = re.sub("\s+('s)", "\\1", text)
    text = text.replace(" - ", "-")
    return text


def tokenize(text: str) -> List[str]:
    """
    Tokenize a text with the English spaCy tokenizer.

    Args:
        text: the text to be tokenized

    Returns: the list of tokens in the string

    """
    """ Tokenize a string with the English spaCy tokenizer. """
    doc = nlp(text)
    tokens = [t.orth_ for t in doc]
    return tokens


def extract_referents_from_xml_tagged_strings(strings: List[str]) -> Generator[Dict, None, None]:
    """
    Extracts coreference information from strings with coreference tags, such as
    <ref id=0>Schools</ref> should not allow <ref id=1>junk food</ref>
    to be sold on campus but <ref id=1>it</ref> generates money for schools

    Args:
        strings: the xml strings to be parsed

    Returns: a generator with coreference dictionaries

    """
    re_tagged_referent = re.compile(
        r"<ref[ ]+id=(?P<id>(\?|-?\d+))[ ]*>(?P<string>.+?)</ref>")
    for string in strings:
        # print(string)
        spans = []
        s_scrubbed = string
        while True:
            m = re_tagged_referent.search(s_scrubbed)
            if not m:
                break
            matched_string = m.group("string")
            matched_id = m.group("id")
            s_scrubbed = s_scrubbed[:m.start(0)] + matched_string + s_scrubbed[m.end(0):]
            spans.append({"start": m.start(),
                          "end": m.start() + len(matched_string),
                          "str_": matched_string,
                          "id": matched_id})
        print(spans)
        yield {"text": s_scrubbed, "refs": spans}
