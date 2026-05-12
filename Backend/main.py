

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
import pdfplumber
import yake
import io

app = FastAPI()

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow requests from the React frontend running on localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)


print("Loading summarization model...")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6"
print("Model ready!")

# ── Request/Response schemas ──────────────────────────────────────────────────
class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    summary: str
    keywords: list[str]

# ── Keyword extraction helper ─────────────────────────────────────────────────
# Uses YAKE (Yet Another Keyword Extractor) — lightweight, no model needed

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
    # Truncate to first 1024 words to stay within model limits
    words = text.split()
    if len(words) > 1024:
        text = " ".join(words[:1024])

    # min/max length control how long the summary is
    result = summarizer(text, max_length=150, min_length=40, do_sample=False)
    return result[0]["summary_text"]

# ── ENDPOINT 1: POST /summarize ───────────────────────────────────────────────
# Accepts plain text, returns summary + keywords
@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    summary = summarize_text(request.text)
    keywords = extract_keywords(request.text)

    return SummarizeResponse(summary=summary, keywords=keywords)

#  ENDPOINT 2: POST /upload-pdf 
# Accepts a PDF file upload, extracts text, returns summary + keywords
@app.post("/upload-pdf", response_model=SummarizeResponse)
async def upload_pdf(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Read file bytes into memory
    contents = await file.read()

    # Extract text using pdfplumber
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