
# GenAI Document Parser


## Context: 
IDP is being seen as a very common use case amongst customers. While Textract and other OCR technologies work well with simpler documents where format remains static (such as Tax Statements) but becomes a problem for more complex documents with varying formats (such as Bank Statements and Invoices). A lot of customers struggle with accuracy, maintenance of complex post processing rules/models and accuracy. Additional challenge is support for non-English languages. The vision capabilities of Claude 3 have been seen to be working well especially for complex documents of English as well as Non-English languages.
 
 
## Key Features:
Extraction of data from banks statements: The parser extracts summary information and transaction details from the bank statements. It also reconciles closing balance with transaction details

Extraction of data from identity documents: The parser extracts information from identity documents in many different languages. Currently it has been tested to work on English, Japanese and Arabic language documents.


## Pre-requisites:
Python 3.9 or above


## How to setup:
Clone the GIT repositry

```
git clone https://github.com/aws-samples/documentparser-bedrock
cd documentparser-bedrock
```

Create and activate virtual environment  
```
python3 -m venv ./.venv
source ./.venv/bin/activate
```

Install dependencies
```
pip install -r requirements.txt
```

Run streamlit
```
streamlit run analyzer_streamlit.py --server.port 8080
```


## Samples:
![Image1](/static/extraction-screenshot1.png)
![Image2](/static/extraction-screenshot2.png)
![Image3](/static/extraction-screenshot3.png)
