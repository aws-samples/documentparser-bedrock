import boto3
import os
import base64
import botocore
import json
import uuid
import fitz #for converting pdf to image

bluePrintConfig = {}
bluePrintList = ""

def multi_page_pdf2image(pdfBytes, pdfPath, outputPath):
   #split the multi page PDF into images if the directory does not exist already
    if not os.path.isdir(outputPath):
        os.makedirs(outputPath)
        
        pdfStream = None
        if pdfPath is not None: 
            pdfStream = fitz.open(pdfPath, filetype = "pdf")
        else:
            pdfStream = fitz.open(stream = pdfBytes, filetype = "pdf")
        
        for idx, page in enumerate(pdfStream):
            pix = page.get_pixmap(dpi=100) 
            the_page_bytes = pix.pil_tobytes(format="jpeg")
            with open(os.path.join(outputPath, "page-%s.jpg"%idx), "wb") as outf:
                outf.write(the_page_bytes)

def analyzeDoc(imageConvPath, analyzerPrompt):
    encodedImages = []
    
    #Encode the images
    for filename in os.listdir(imageConvPath):
        filePath = os.path.join(imageConvPath, filename)
        if os.path.isfile(filePath) and '.jpg' in filename:
            with open(filePath, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode("utf-8")
                encodedImages.append(encoded_image)

    parsedDoc = call_bedrock(modelId="anthropic.claude-3-sonnet-20240229-v1:0", maxTokens = 32768, encodedImages = encodedImages, textPrompt = analyzerPrompt)
    return parsedDoc
    
def classifyDoc(pdfDocIo, pdfDocPath):
    if bluePrintList == "":
        getConfig()
        
    #print(f"Blueprints: {bluePrintList}")
        
    returnVal = {}
    classificationPrompt = "classify the document type between " + bluePrintList + " and Others. Only return document type and nothing else"
    #print(classificationPrompt)
    
    imageConvPath = ""
    if pdfDocPath is not None:
        imageConvPath = os.path.join(os.path.dirname(pdfDocPath), 'output_' + os.path.splitext(os.path.basename(pdfDocPath))[0], 'image_conversion/')
    else:
        imageConvPath = os.path.join("pdf_documents", 'output_' + os.path.splitext(pdfDocIo['fileName'])[0], 'image_conversion/')
        
    returnVal['imageConvPath'] = imageConvPath
    multi_page_pdf2image(pdfBytes = pdfDocIo['fileData'], pdfPath = pdfDocPath, outputPath = imageConvPath)
    
    #encoding of images
    cnt = 0
    encodedImages = []
    for filename in os.listdir(imageConvPath):
        filePath = os.path.join(imageConvPath, filename)
        if os.path.isfile(filePath) and '.jpg' in filename:
            cnt = cnt + 1
            with open(filePath, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode("utf-8")
    
                encodedImages.append(encoded_image)
            if cnt == 2: #max of 2 pages for the classification:    
                break

    returnVal['docType'] = call_bedrock(modelId='anthropic.claude-3-sonnet-20240229-v1:0', maxTokens=512, encodedImages=encodedImages, textPrompt=classificationPrompt)
    returnVal['docTypeDisplayName'] = bluePrintConfig['bluePrints'][returnVal['docType']]['displayName']
    returnVal['textPrompt'] = bluePrintConfig['bluePrints'][returnVal['docType']]['textPrompt']
    
    return(returnVal)

def call_bedrock(modelId, maxTokens, encodedImages, textPrompt):
    session = boto3.session.Session()
    bedrockClient = session.client(service_name = 'bedrock-runtime', config = botocore.config.Config(read_timeout = 6000))    

    #initialize the prompt
    bodyContent = []
    promptBody = {
                    "type": "text",
                    "text": textPrompt
                }

    bodyContent.append(promptBody)
    
    #construct the prompt with images and text
    for image in encodedImages:
        bodyContent.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image
            }
        })

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": maxTokens,
        "messages": [
            {
                "role": "user",
                "content": bodyContent
            }
        ]
    }
    
    try:
        response = bedrockClient.invoke_model(
            modelId=modelId,
            body=json.dumps(request_body),
        )
    
        # Process and print the response
        result = json.loads(response.get("body").read())
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])
    
        print("Invocation details:")
        print(f"- The input length is {input_tokens} tokens.")
        print(f"- The output length is {output_tokens} tokens.")
        print(f"- The model returned {len(output_list)} response(s):")
    
        return output_list[0]["text"]
    except botocore.exceptions.ClientError as err:
        raise

def getConfig():
    import yaml
    
    global bluePrintConfig
    global bluePrintList

    with open('blueprints.yaml', 'r') as file:
        bluePrintConfig = yaml.safe_load(file)
    
    if 'bluePrints' in bluePrintConfig:    
        bluePrintList = ', '.join([str(elem) for elem in list(bluePrintConfig['bluePrints'].keys())])

if __name__ == "__main__":
    docTypeOutput = classifyDoc(pdfDocIo = {'fileName': None, 'fileData': None}, pdfDocPath = "pdf_documents/70.pdf")
    print(docTypeOutput)
    
    analyzerOutput = analyzeDoc(imageConvPath=docTypeOutput['imageConvPath'], analyzerPrompt=docTypeOutput['textPrompt'])
    print(json.loads(analyzerOutput))
