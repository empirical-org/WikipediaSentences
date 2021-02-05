import streamlit as st

from quillnlp.grammar.bing import classify_correction


st.sidebar.title("Quill NLP Tools")
st.sidebar.markdown(
    """
    Grammar correction classification
    """
)

st.title("Error classification")

original_sentence = st.text_input("Original sentence", value='')
corrected_sentence = st.text_input("Corrected sentence", value='')


if len(original_sentence) > 0 and len(corrected_sentence) > 0:

    errors = classify_correction(original_sentence, corrected_sentence)
    st.write(errors)

