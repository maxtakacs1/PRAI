from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional, List
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PRAI API")

app = FastAPI(title="PRAI API", version="0.1.0")
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#--- Helper functions for invoke ---#
# TODO: Add helper functions here\
def process_file(file):
    logger.info("Processing file")
    # TODO: Add file processing logic here
    return

def process_url(url):
    logger.info("Processing URL")
    # TODO: Add URL processing logic here
    return

def web_scrape(topic):
    logger.info("Web scraping")
    # TODO: Add web scraping logic here
    return

#--- Helper functions for upload_reference ---#
def process_reference(reference):
    logger.info("Processing reference")
    # TODO: Add reference processing logic here
    return

#--- Routes ---#
@app.get("/")
def read_root():
    logger.info("API is running!")
    return {"message": "The API is running!"}

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.get("/invoke")
async def invoke(
    source_choice: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    url: Optional[List[str]] = Form(None),
    text: Optional[str] = Form(None),
    topic: str = Form(...),
    length: str = Form(...),
    references: Optional[str] = Form(None),
):
    logger.info("Invoke endpoint called")
    file_flag = False
    url_flag = False
    auto_flag = False
    if source_choice == "file":
        logger.info("File uploaded")
        file_flag = True
    elif source_choice == "url":
        logger.info("URL provided")
        url_flag = True
    elif source_choice == "text":
        logger.info("Text provided")
    elif source_choice == "auto":
        logger.info("Auto-sourcing mode")
        auto_flag = True
        url_flag = True
    else:
        logger.error("Invalid source choice")

    source_info = []
    if file_flag:
        for file in files:
            processed_file = process_file(file)
            source_info.append(processed_file)
    elif url_flag and not auto_flag:
        for u in url:
            processed_url = process_url(u)
            source_info.append(processed_url)
    elif auto_flag:
        auto_process = web_scrape(topic)
        source_info.append(auto_process)
    else:
        processed_text = {"content": text}
        source_info.append(processed_text)
    
    # TODO: send topic and source_info to the model to create an info sheet on the topic based on the source info

    # TODO: use the info sheet and length selection to generate a first draft of the article

    # TODO: use the first draft of the article and the references to generate a final draft of the article in the tone of the references

    return

@app.post("/uploadreference")
async def upload_reference(
    reference: List[UploadFile] = File(...)
):
    logger.info("Reference uploaded")
    for ref in reference:
        processed_reference = process_reference(ref)
        # TODO: store processed reference in database
    return
            
    
