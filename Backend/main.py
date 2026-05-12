import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
import pdfplumber
import yake
import io

app = FastAPI()

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Lazy model loading ────────────────────────────────────────────────────────
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        print("Loading summarization model...")
        summarizer = pipeline("summarization", model="t5-small", device=-1)
        print("Model ready!")
    return summarizer

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

    result = get_summarizer()(text, max_length=150, min_length=40, do_sample=False)
    return result[0]["summary_text"]

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