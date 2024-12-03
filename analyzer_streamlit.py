import streamlit as st
import json
import pandas as pd
import json_repair
import analyzer_main as anam1

classificationModelId = "us.anthropic.claude-3-sonnet-20240229-v1:0"
extractionModelId = "us.anthropic.claude-3-5-sonnet-20241022-v2:0" #default
maxTokens = 2048 #default

st.title("Document Analyzer")

@st.cache_data()
def runClassifyDoc(uploaded_file):
    docTypeOutput = anam1.classifyDoc(bedrockModelId = classificationModelId, extractionModelId = extractionModelId, pdfDocIo = {'fileName': uploaded_file.name, 'fileData': uploaded_file.getvalue()}, pdfDocPath = None)
    return docTypeOutput

option = st.selectbox(
    "Which Bedrock FM would you like to use?",
    #("Claude-3-Sonnet", "Claude-3-Haiku", "Claude-3.5-Sonnet-v1", "Claude-3.5-Sonnet-v2", "Llama 3.2 90B"),
    ("Claude-3-Sonnet", "Claude-3-Haiku", "Claude-3.5-Sonnet-v1", "Claude-3.5-Sonnet-v2"),
    index=3
)

if option == "Claude-3-Sonnet":
    extractionModelId = "us.anthropic.claude-3-sonnet-20240229-v1:0"
    maxTokens = 4096
elif option == "Claude-3-Haiku":
    extractionModelId = "us.anthropic.claude-3-haiku-20240307-v1:0"
    maxTokens = 4096
elif option == "Claude-3.5-Sonnet-v1":
    extractionModelId = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"
    maxTokens = 4096
elif option == "Claude-3.5-Sonnet-v2":
    extractionModelId = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    maxTokens = 8192
elif option == "Llama 3.2 90B":
    extractionModelId = "us.meta.llama3-2-90b-instruct-v1:0"
    maxTokens = 2048
    
#st.write("Inference Profile Id:", extractionModelId)
        
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
            modelOutput = anam1.analyzeDoc(bedrockModelId = extractionModelId, maxTokens = maxTokens, imageConvPath=docTypeOutput['imageConvPath'], specificFileName = "", analyzerPrompt=docTypeOutput['textPrompt']['subType1'])
            st.json(json_repair.loads(modelOutput))
        else:
            for pageNo in docTypeOutput['subTypeClassification']:
                if docTypeOutput['subTypeClassification'][pageNo] != "Others":
                    modelOutput = anam1.analyzeDoc(bedrockModelId = extractionModelId, maxTokens = maxTokens, imageConvPath=docTypeOutput['imageConvPath'], specificFileName = pageNo, analyzerPrompt=docTypeOutput['textPrompt'][docTypeOutput['subTypeClassification'][pageNo]])
            
                    st.markdown(f"**{pageNo}** of type **{docTypeOutput['subTypeClassification'][pageNo]}**")
                    st.json(json_repair.loads(modelOutput))
  
    if st.button("Extract information as RAW Text"):
        if docTypeOutput['docClassifierType'] == 'multi_page':
            modelOutput = anam1.analyzeDoc(bedrockModelId = extractionModelId, maxTokens = maxTokens, imageConvPath=docTypeOutput['imageConvPath'], specificFileName = "", analyzerPrompt=docTypeOutput['textPrompt']['subType1'])
            st.write(modelOutput)
        else:
            for pageNo in docTypeOutput['subTypeClassification']:
                if docTypeOutput['subTypeClassification'][pageNo] != "Others":
                    modelOutput = anam1.analyzeDoc(bedrockModelId = extractionModelId, maxTokens = maxTokens, imageConvPath=docTypeOutput['imageConvPath'], specificFileName = pageNo, analyzerPrompt=docTypeOutput['textPrompt'][docTypeOutput['subTypeClassification'][pageNo]])
            
                    st.markdown(f"**{pageNo}** of type **{docTypeOutput['subTypeClassification'][pageNo]}**")
                    st.write(modelOutput)
                    
    if st.button("Extract information as Table"):
        if docTypeOutput['docClassifierType'] == 'multi_page':
            modelOutput = anam1.analyzeDoc(bedrockModelId = extractionModelId, maxTokens = maxTokens, imageConvPath=docTypeOutput['imageConvPath'], specificFileName = "", analyzerPrompt=docTypeOutput['textPrompt']['subType1'])
        else:
            modelOutput = anam1.analyzeDoc(bedrockModelId = extractionModelId, maxTokens = maxTokens, imageConvPath=docTypeOutput['imageConvPath'], specificFileName = "", analyzerPrompt=docTypeOutput['textPrompt']['subType1'])
        
        if docTypeOutput['docType'] == 'bankStatement':
            summary = json.loads(modelOutput)['summary']
            details = json.loads(modelOutput)['transactions']
            #aggregates = json.loads(modelOutput)['aggregates']
        
            st.dataframe(summary)
            st.dataframe(details)
            #st.dataframe(aggregates)
        else:
            st.write(modelOutput)
