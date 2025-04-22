import io
import os
import pathlib
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List, Optional
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import PyPDF2
import docx
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

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

# mount PoC folder so HTML/JS/CSS under /poc/* are served
poc_dir = pathlib.Path(__file__).parents[2] / "PoC"
app.mount("/poc", StaticFiles(directory=str(poc_dir), html=True), name="poc")

#--- Helper functions for invoke ---#
def process_file(file: UploadFile):
    logger.info(f"Processing file: {file.filename}")
    ext = os.path.splitext(file.filename)[1].lower()
    data = file.file.read()
    stream = io.BytesIO(data)
    text = ""
    if ext == ".pdf":
        reader = PyPDF2.PdfReader(stream)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n\n"
    elif ext == ".docx":
        document = docx.Document(stream)
        for para in document.paragraphs:
            text += para.text + "\n\n"
    else:
        try:
            text = data.decode("utf-8")
        except:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
    # simple markdown conversion (preserve paragraphs)
    md = text.strip()
    return {"filename": file.filename, "content": md}

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

@app.post("/invoke")
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

# PoC endpoint
@app.post("/poc/invoke")
async def poc_invoke(
    source_file: UploadFile = File(...),
    topic: str = Form(...),
    length: str = Form(...),
    style_file: UploadFile = File(...),
):
    logger.info("PoC invoke called")
    src = process_file(source_file)
    stl = process_file(style_file)

    llm = ChatOpenAI(temperature=0.7)
    # Define length_directions based on length
    length_directions = ""
    if length == "LinkedIn Article":
        length_directions = "Somewhere between 1500 and 2500 words, and it should be a professional article that is easy to read and understand. It should focus on engaging the reader and providing valuable insights."
    elif length == "Press Release":
        length_directions = "Somewhere between 300 and 500 words, and it should be a concise and informative announcement that captures the essence of the news being shared. It should be written in a clear and engaging manner."
    elif length == "LinkedIn Post":
        length_directions = "Somewhere between 100 and 300 words, and it should be a short and engaging post that captures the reader's attention. It should be written in a conversational tone and encourage interaction."
    elif length == "Opinion Article":
        length_directions = "Somewhere between 300 and 550 words, and it should be a well-reasoned and thought-provoking article that presents a clear opinion on the topic. It should be written in a persuasive and engaging tone similar to that of the reference and include relevant examples."
    else:
        length_directions = "Somewhere between 1000 and 1500 words, and it should be a well-structured and informative article that provides valuable insights on the topic. It should be written in a professional tone and include relevant examples."

    # 1) Info sheet generation
    prompt1 = (
        f"You are an AI assistant. Create an information sheet about '{topic}', "
        f" for a final paper of {length} length to be written on it, and the specific needs are exactly '{length_directions}', based on the following text (markdown):\n\n{src['content']}"
    )
    resp1 = llm([HumanMessage(content=prompt1)])
    info_sheet = resp1[0].text.strip()

    # 2) Final draft generation
    prompt2 = (
        f"You are an AI assistant. Using the following information sheet (markdown):\n\n{info_sheet}\n\n"
        f"Write a final article of {length} length, which means specifically '{length_directions}', in the writing style matching this reference text (markdown):\n\n{stl['content']}"
    )
    resp2 = llm([HumanMessage(content=prompt2)])
    final_draft = resp2[0].text.strip()

    return JSONResponse({
        "topic": topic,
        "length": length,
        "info_sheet": info_sheet,
        "final_draft": final_draft
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


