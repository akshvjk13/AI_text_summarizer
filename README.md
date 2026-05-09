# AI-Based Text Summarization Platform

## Project Overview

The AI-Based Text Summarization Platform is a full-stack NLP web application that generates concise summaries from long textual content and PDF documents using HuggingFace Transformers.

The application allows users to:

* Paste long text for summarization
* Upload PDF documents
* Generate AI-powered summaries
* Extract important keywords from content
* Download generated summaries as PDF files

This project was built using React, Tailwind CSS, FastAPI, and HuggingFace Transformers.

---

# Features

## Core Features

* AI-powered text summarization
* PDF upload and processing
* Keyword extraction
* Export summary as PDF
* Clean and responsive UI
* FastAPI backend integration
* HuggingFace NLP model integration

---

# Technology Stack

## Frontend

* React.js
* Vite
* Tailwind CSS
* Axios

## Backend

* Python FastAPI
* HuggingFace Transformers
* Uvicorn

## NLP & File Processing

* facebook/bart-large-cnn
* pdfplumber
* YAKE

---

# Project Structure

```bash
AI Summarizer/

├── Backend/
│   ├── main.py
│   └── requirements.txt
│
├── Frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
└── README.mdv
```
---

# Backend Setup Instructions

## Step 1: Open Backend Folder

```bash
cd Backend
```

## Step 2: Create Virtual Environment

```bash
python -m venv venv
```

## Step 3: Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

After activation, your terminal should display:

```bash
(venv)
```

## Step 4: Install Required Python Packages

```bash
pip install fastapi
pip install uvicorn
pip install transformers
pip install torch
pip install sentencepiece
pip install pdfplumber
pip install yake
pip install python-multipart
```

## Step 5: Run Backend Server

```bash
uvicorn main:app --reload
```

Backend will run at:

```bash
http://127.0.0.1:8000
```

FastAPI API documentation:

```bash
http://127.0.0.1:8000/docs
```

---

# Frontend Setup Instructions

## Step 1: Open Frontend Folder

```bash
cd Frontend
```

## Step 2: Install Dependencies

```bash
npm install
```

## Step 3: Start Frontend Server

```bash
npm run dev
```

Frontend will run at:

```bash
http://localhost:5173
```

---

