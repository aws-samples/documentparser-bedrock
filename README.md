
# GenAI Document Parser

 
Context:
 
IDP is being seen as a very common use case amongst customers. While Textract and other OCR technologies work well with simpler documents where format remains static (such as Tax Statements) but becomes a problem for more complex documents with varying formats (such as Bank Statements and Invoices). A lot of customers struggle with accuracy, maintenance of complex post processing rules/models and accuracy. Additional challenge is support for non-English languages. The vision capabilities of Claude 3 have been seen to be working well especially for complex documents of English as well as Non-English languages.
 


 
## Key Features:
PDF Upload: Users can upload bank statements in PDF format directly to the application. In this demo we have added some sample bank statements.
Data Extraction: The parser extracts summary information, transaction details, and aggregate metrics from the bank statements.
Output Formats: Extracted data is presented in both JSON and tabular formats for easy analysis and integration with other systems.
Efficiency: The automated parsing process eliminates the need for manual data entry, saving time and reducing errors.

Run: python3 -m streamlit run analyzer_streamlit.py and then upload the bank statements or Identity documents.
