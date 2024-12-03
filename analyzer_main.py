import boto3
import os
import base64
import botocore
import json
import uuid
import shutil
import fitz #for converting pdf to image

bluePrintConfig = {}
bluePrintList = ""

def multi_page_pdf2image(pdfBytes, pdfPath, outputPath, bedrockModelId):
   #split the multi page PDF into images (up to 20 pages) if the directory does not exist already
        
    if 'llama3' in bedrockModelId and os.path.isdir(outputPath):
        shutil.rmtree(outputPath)
       
    if not os.path.isdir(outputPath):
        pageNo = 0
        
        os.makedirs(outputPath)
        
        pdfStream = None
        if pdfPath is not None: 
            pdfStream = fitz.open(pdfPath, filetype = "pdf")
        else:
            pdfStream = fitz.open(stream = pdfBytes, filetype = "pdf")
        
        for idx, page in enumerate(pdfStream):
            pageNo = pageNo + 1
            
            if pageNo <= 20:
                file_name = ""
                if 'llama3' in bedrockModelId:
                    pix = page.get_pixmap(dpi=100) 
                    the_page_bytes = pix.pil_tobytes(format="png")
                    file_name = "page-%s.png"%str(idx).rjust(2,'0')
                else:
                    pix = page.get_pixmap(dpi=300) 
                    the_page_bytes = pix.pil_tobytes(format="jpeg")
                    file_name = "page-%s.jpg"%str(idx).rjust(2,'0')
                    
                with open(os.path.join(outputPath, file_name), "wb") as outf:
                    outf.write(the_page_bytes)

def analyzeDoc(bedrockModelId, maxTokens, imageConvPath, specificFileName, analyzerPrompt):
    encodedImages = []
    
    #Encode the images
    cnt = 0
    for filename in sorted(os.listdir(imageConvPath)):
        filePath = os.path.join(imageConvPath, filename)
        if os.path.isfile(filePath) and ('.jpg' in filename or '.png' in filename ) and (filename == specificFileName or specificFileName == ""):
            cnt = cnt + 1
            
            with open(filePath, "rb") as f:
                encoded_image = f.read()
                encodedImages.append(encoded_image)
                
            if cnt >= 5:
                break

    parsedDoc = call_bedrock(modelId = bedrockModelId, extractionModelId = bedrockModelId, maxTokens = maxTokens, encodedImages = encodedImages, textPrompt = analyzerPrompt)
    return parsedDoc
    
def classifyDoc(bedrockModelId, extractionModelId, pdfDocIo, pdfDocPath):
    if bluePrintList == "":
        getConfig()
        
    returnVal = {}
    subTypeClassification = {}
    
    imageConvPath = ""
    if pdfDocPath is not None:
        imageConvPath = os.path.join(os.path.dirname(pdfDocPath), 'output_' + os.path.splitext(os.path.basename(pdfDocPath))[0], 'image_conversion/')
    else:
        imageConvPath = os.path.join("pdf_documents", 'output_' + os.path.splitext(pdfDocIo['fileName'])[0], 'image_conversion/')

    classificationPrompt = "classify the document type between " + bluePrintList + " and Others based on the input image and file path: "
    classificationPrompt = classificationPrompt + imageConvPath + ". Only return document type and nothing else"
    
    returnVal['imageConvPath'] = imageConvPath
    multi_page_pdf2image(pdfBytes = pdfDocIo['fileData'], pdfPath = pdfDocPath, outputPath = imageConvPath, bedrockModelId = extractionModelId)
    
    #encoding of images
    cnt = 0
    encodedImages = []
    for filename in sorted(os.listdir(imageConvPath)):
        filePath = os.path.join(imageConvPath, filename)
        if os.path.isfile(filePath) and '.jpg' in filename:
            cnt = cnt + 1
            print(filename)
            with open(filePath, "rb") as f:
                encoded_image = f.read()
    
                encodedImages.append(encoded_image)
            if cnt == 2: #max of 2 pages for the classification:    
                break

    returnVal['docType'] = call_bedrock(modelId=bedrockModelId, extractionModelId = extractionModelId, maxTokens=256, encodedImages=encodedImages, textPrompt=classificationPrompt)
    
    if returnVal['docType'] != "Others":
        returnVal['docTypeDisplayName'] = bluePrintConfig['bluePrints'][returnVal['docType']]['displayName']
        returnVal['docClassifierType'] = bluePrintConfig['bluePrints'][returnVal['docType']]['type']
        returnVal['textPrompt'] = bluePrintConfig['bluePrints'][returnVal['docType']]['textPrompt']
        
        if returnVal['docClassifierType'] == 'multi_page':
            returnVal['subTypeList'] = ""
            returnVal['subTypeClassification'] = {}
        else:
            subTypeList = ', '.join([str(elem) for elem in list(bluePrintConfig['bluePrints'][returnVal['docType']]['textPrompt'].keys())])
            returnVal['subTypeList'] = subTypeList
            
            subTypeClassification = {}
            classificationPrompt = "classify the document type between " + subTypeList + " and Others. Only return document type and nothing else"
            
            #encoding of images
            cnt = 0
            for filename in sorted(os.listdir(imageConvPath)):
                filePath = os.path.join(imageConvPath, filename)
                if os.path.isfile(filePath) and '.jpg' in filename:
                    cnt = cnt + 1
                    with open(filePath, "rb") as f:
                        encoded_image = base64.b64encode(f.read()).decode("utf-8")
                        encodedImages = []
                        encodedImages.append(encoded_image)
                        
                        if cnt > 5: #max of 5 pages for the sub classification:
                            break
                    
                    subTypeClassification[filename] = call_bedrock(modelId=bedrockModelId, extractionModelId = extractionModelId, maxTokens=512, encodedImages=encodedImages, textPrompt=classificationPrompt)
                    if subTypeClassification[filename] not in subTypeList:
                        subTypeClassification[filename] = 'Others'
    
            returnVal['subTypeClassification'] = subTypeClassification
            
            #print(classificationPrompt)
            print(subTypeClassification)
        
    return(returnVal)

def call_bedrock(modelId, extractionModelId, maxTokens, encodedImages, textPrompt):
    session = boto3.session.Session()
    bedrockClient = session.client(service_name = 'bedrock-runtime', config = botocore.config.Config(read_timeout = 6000))    

    #initialize the prompt
    bodyContent = [
            {"text": textPrompt}
        ]
    
    if maxTokens <= 512:    
        systemContent = [
                {"text": "Do not make any assumptions and always return accurate information"}
            ]
    else:
        systemContent = [
                {"text": "Your task is to extract or classify the data from input images with the highest accuracy following"}
            ]


    for image in encodedImages:
        bodyContent.append({
            "image": {
                "format": "png" if 'llama3' in extractionModelId else "jpeg",
                "source": {"bytes": image}
            }
        })
    
    if 'llama3' in extractionModelId:
        inferenceConfig = {"temperature": 0}
    else:
        inferenceConfig = {"maxTokens": maxTokens, "temperature": 0, "topP": 0.999}
    
    try:
        response = bedrockClient.converse(
            modelId=modelId,
            messages=[
                    {
                        "role": "user",
                        "content": bodyContent
                    }
                ],
            system = systemContent,
            inferenceConfig = inferenceConfig
        )
    
        # Process and print the response
        input_tokens = response["usage"]["inputTokens"]
        output_tokens = response["usage"]["outputTokens"]
        output_list = response['output']['message']['content']
    
        print("Invocation details:")
        print(f"- The input length is {input_tokens} tokens.")
        print(f"- The output length is {output_tokens} tokens.")
        print(f"- The model returned {len(output_list)} response(s):")
        #print(f"- Output Response is {output_list}")
    
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

#if __name__ == "__main__":
    #docTypeOutput = classifyDoc(bedrockModelId = "", pdfDocIo = {'fileName': None, 'fileData': None}, pdfDocPath = "pdf_documents/70.pdf")
    #print(docTypeOutput)
    
    #analyzerOutput = analyzeDoc(imageConvPath=docTypeOutput['imageConvPath'], analyzerPrompt=docTypeOutput['textPrompt'])
    #print(json.loads(analyzerOutput))
