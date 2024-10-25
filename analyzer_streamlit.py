import streamlit as st
import json
import pandas as pd
import analyzer_main as anam1

st.title("Document Analyzer")

@st.cache_data()
def runClassifyDoc(uploaded_file):
    docTypeOutput = anam1.classifyDoc(pdfDocIo = {'fileName': uploaded_file.name, 'fileData': uploaded_file.getvalue()}, pdfDocPath = None)
    return docTypeOutput

uploaded_file = st.file_uploader("Upload a document in pdf format", type=["pdf", "png", "jpeg"])

if uploaded_file is not None:
    docTypeOutput = runClassifyDoc(uploaded_file)
    
    if 'docClassifierType' in docTypeOutput:
        if docTypeOutput['docClassifierType'] == 'multi_page':
            st.markdown(f"Type of document is **{docTypeOutput['docTypeDisplayName']}**")
        else:
            st.markdown(f"Type of document is **{docTypeOutput['docTypeDisplayName']}** with sub types: **{docTypeOutput['subTypeList']}**")
    else:
        st.markdown(f"Type of document is **{docTypeOutput['docType']}**")
    
    if st.button("Extract information as JSON"):
        if docTypeOutput['docClassifierType'] == 'multi_page':
            modelOutput = anam1.analyzeDoc(imageConvPath=docTypeOutput['imageConvPath'], specificFileName = "", analyzerPrompt=docTypeOutput['textPrompt']['subType1'])
            st.json(json.loads(modelOutput))
        else:
            for pageNo in docTypeOutput['subTypeClassification']:
                if docTypeOutput['subTypeClassification'][pageNo] != "Others":
                    modelOutput = anam1.analyzeDoc(imageConvPath=docTypeOutput['imageConvPath'], specificFileName = pageNo, analyzerPrompt=docTypeOutput['textPrompt'][docTypeOutput['subTypeClassification'][pageNo]])
            
                    st.markdown(f"**{pageNo}** of type **{docTypeOutput['subTypeClassification'][pageNo]}**")
                    st.json(json.loads(modelOutput))
    
    if st.button("Extract information as Table"):
        if docTypeOutput['docClassifierType'] == 'multi_page':
            modelOutput = anam1.analyzeDoc(imageConvPath=docTypeOutput['imageConvPath'], specificFileName = "", analyzerPrompt=docTypeOutput['textPrompt']['subType1'])
        else:
            modelOutput = anam1.analyzeDoc(imageConvPath=docTypeOutput['imageConvPath'], specificFileName = "", analyzerPrompt=docTypeOutput['textPrompt']['subType1'])
        
        if docTypeOutput['docType'] == 'bankStatement':
            summary = json.loads(modelOutput)['summary']
            details = json.loads(modelOutput)['transactions']
            #aggregates = json.loads(modelOutput)['aggregates']
        
            st.dataframe(summary)
            st.dataframe(details)
            #st.dataframe(aggregates)
        else:
            st.write(modelOutput)
