import streamlit as st

from quillnlp.grammar.grammarcheck import SpaCyGrammarChecker


@st.cache(allow_output_mutation=True)
def load_checker(name):
    checker = SpaCyGrammarChecker(name)
    return checker



st.sidebar.title("Quill NLP Tools")
st.sidebar.markdown(
    """
    Grammar rules
    """
)

st.title("Grammar Check")

sentence = st.text_area("Type in a sentence", value='')

MODEL = "models/spacy_grammar"
checker = load_checker(MODEL)


if len(sentence) > 0:

    errors = checker.check(sentence)
    error_types = set([e[2] for e in errors])

    st.header("Grammar errors")
    st.write(error_types)

    st.header("Corrections")
    text = sentence

    # sort errors from end to start, because we're going to manipulate the string
    errors = sorted(errors, key=lambda e: e[1], reverse=True)
    for error in errors:
        start_idx = error[1]
        end_idx = start_idx + len(error[0])

        text = text[:start_idx] + f"~~{text[start_idx:end_idx]}~~" + text[end_idx:]

    st.write(text)
    # st.write([x.tag_ for x in doc])
    # st.write([x.pos_ for x in doc])


