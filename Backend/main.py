import os
import requests as req
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pdfplumber
import yake
import io

app = FastAPI()

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── HuggingFace Inference API ─────────────────────────────────────────────────
HF_API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-6-6"
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# ── Request/Response schemas ──────────────────────────────────────────────────
class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    summary: str
    keywords: list[str]

# ── Keyword extraction helper ─────────────────────────────────────────────────
def extract_keywords(text: str, max_keywords: int = 8) -> list[str]:
    try:
        kw_extractor = yake.KeywordExtractor(
            lan="en",
            n=1,
            dedupLim=0.4,
            dedupFunc="seqm",
            top=20,
        )
        keywords = kw_extractor.extract_keywords(text)
        keywords.sort(key=lambda x: x[1])
        kw_strings = [kw[0].title() for kw in keywords]

        final = []
        for kw in kw_strings:
            kw_lower = kw.lower()
            if not any(kw_lower in selected.lower() and kw_lower != selected.lower()
                       for selected in final):
                final.append(kw)
            if len(final) >= max_keywords:
                break

        return final

    except Exception:
        return []

# ── Summarization helper ──────────────────────────────────────────────────────
def summarize_text(text: str) -> str:
    words = text.split()
    if len(words) > 512:
        text = " ".join(words[:512])

    response = req.post(
        HF_API_URL,
        headers=HF_HEADERS,
        json={
            "inputs": f"summarize: {text}",
        },
        timeout=60
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"HuggingFace API error: {response.text}")

    result = response.json()

    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", result[0].get("summary_text", ""))
    
    raise HTTPException(status_code=500, detail="Unexpected response from HuggingFace API")

# ── ENDPOINT 1: POST /summarize ───────────────────────────────────────────────
@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    summary = summarize_text(request.text)
    keywords = extract_keywords(request.text)

    return SummarizeResponse(summary=summary, keywords=keywords)

# ── ENDPOINT 2: POST /upload-pdf ─────────────────────────────────────────────
@app.post("/upload-pdf", response_model=SummarizeResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    contents = await file.read()

    try:
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            extracted_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read PDF: {str(e)}")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF. The file may be scanned or image-based.")

    summary = summarize_text(extracted_text)
    keywords = extract_keywords(extracted_text)

    return SummarizeResponse(summary=summary, keywords=keywords)