import streamlit as st
import base64

from quillnlp.preprocessing.srl import perform_srl, process_srl_results


st.sidebar.title("Quill NLP Tools")
st.sidebar.markdown(
    """
    SRL & Clustering
    """
)

st.title("Data Preprocessing")

st.write("Please enter the prompt and upload a txt file with one response per line.")

prompt = st.text_input("Prompt:", value="")

uploaded_file = st.file_uploader("Choose a file", type=['txt'])
if uploaded_file is not None:
    responses = [line.strip() for line in uploaded_file]

    srl_results = perform_srl(responses, prompt)
    final_results = process_srl_results(srl_results)
    result_string = "\n".join(["\t".join([str(x) for x in item]) for item in final_results])


    b64 = base64.b64encode(result_string.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download tab-separated file</a> (right-click and save as &lt;some_name&gt;.tsv)'
    st.markdown(href, unsafe_allow_html=True)

