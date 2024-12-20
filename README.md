
# GenAI Document Parser


## Context: 
IDP is being seen as a very common use case amongst customers. While Textract and other OCR technologies work well with simpler documents where format remains static (such as Tax Statements) but becomes a problem for more complex documents with varying formats (such as Bank Statements and Invoices). A lot of customers struggle with accuracy, maintenance of complex post processing rules/models and accuracy. Additional challenge is support for non-English languages. The vision capabilities of **Claude 3/3.5 Models from Anthropic** and **Nova models from Amazon** have been seen to be working well especially for complex documents of English as well as Non-English languages.
 
 
## Key Features:
Extraction of data from banks statements: The parser extracts summary information and transaction details from the bank statements. It also reconciles closing balance with transaction details

Extraction of data from identity documents: The parser extracts information from identity documents in many different languages. Currently it has been tested to work on English, Japanese and Arabic language documents.


## Pre-requisites:
Python 3.9 or above


## Setup:
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


### IAM Authentication:
The solution uses AWS SDK for Python (Boto3) to invoke [Amazon Bedrock](https://aws.amazon.com/bedrock/) models. It requires the configuration of AWS credentials in order to work. [Boto3 user guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) has complete details on the same. Depending on the credential method, below code block in **analyzer_main.py** may need to be modified.

![ImageIAMAuth](/static/boto3-credentials.png)


### Setup Access for Amazon Bedrock foundation models:
Access to Amazon Bedrock foundation models isn't granted by default. You can request access, or modify access, to foundation models only by using the Amazon Bedrock console. The solution requires access to **Anthropic - Claude 3 Sonnet** at the minimum as it is used for classifying the documents and depending on the user selection in drop down, can be used for data extraction as well. Please enable other foundation models as per requirement. The [documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) contains step by step guide for the same.


### Run the application:
Run streamlit
```
streamlit run analyzer_streamlit.py --server.port 8080
```


## Samples:
![GIF](/static/extraction-bank-statement.gif)
![Image2](/static/extraction-identity-doc.png)

