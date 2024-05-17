import streamlit as st
import analyzer_main as anam
import json
import pandas as pd

st.title("Document Analyzer")

@st.cache_data()
def runClassifyDoc(uploaded_file):
    docTypeOutput = anam.classifyDoc(pdfDocIo = {'fileName': uploaded_file.name, 'fileData': uploaded_file.getvalue()}, pdfDocPath = None)
    return docTypeOutput

uploaded_file = st.file_uploader("Upload a document in pdf format", type=["pdf", "png", "jpeg"])

if uploaded_file is not None:
    docTypeOutput = runClassifyDoc(uploaded_file)
    st.markdown(f"Type of document is **{docTypeOutput['docTypeDisplayName']}**")
    
    if st.button("Extract information as JSON"):
        modelOutput = anam.analyzeDoc(imageConvPath=docTypeOutput['imageConvPath'], analyzerPrompt=docTypeOutput['textPrompt'])
        st.json(json.loads(modelOutput))
    
    if st.button("Extract information as Table"):
        modelOutput = anam.analyzeDoc(imageConvPath=docTypeOutput['imageConvPath'], analyzerPrompt=docTypeOutput['textPrompt'])
        
        if docTypeOutput['docType'] == 'bankStatement':
            summary = json.loads(modelOutput)['summary']
            details = json.loads(modelOutput)['transactions']
        
            st.dataframe(summary)
            st.dataframe(details)
        else:
            st.write(modelOutput)
