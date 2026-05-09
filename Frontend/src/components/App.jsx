// src/components/App.jsx
// Main app — manages all state and API calls for:
//   1. Text summarization
//   2. PDF upload + summarization
//   3. Keyword extraction (returned alongside summary)
//   4. Export summary as PDF (handled inside SummaryCard)

import { useState } from 'react'
import axios from 'axios'
import Header from './Header'
import TextInput from './TextInput'
import SummaryCard from './SummaryCard'

const BASE_URL = 'http://127.0.0.1:8000'

export default function App() {
  const [inputText, setInputText]   = useState('')
  const [summary, setSummary]       = useState(null)
  const [keywords, setKeywords]     = useState([])
  const [isLoading, setIsLoading]   = useState(false)
  const [error, setError]           = useState(null)
  const [pdfFile, setPdfFile]       = useState(null)   // stores the File object
  const [inputMode, setInputMode]   = useState('text') // 'text' | 'pdf'

  // ── Reset output state before each new request ───────────────────────────
  const resetOutput = () => {
    setSummary(null)
    setKeywords([])
    setError(null)
  }

  // ── Handle text summarization ─────────────────────────────────────────────
  const handleSummarizeText = async () => {
    if (!inputText.trim()) return
    resetOutput()
    setIsLoading(true)
    try {
      const response = await axios.post(`${BASE_URL}/summarize`, { text: inputText })
      setSummary(response.data.summary)
      setKeywords(response.data.keywords || [])
    } catch (err) {
      handleError(err)
    } finally {
      setIsLoading(false)
    }
  }

  // ── Handle PDF upload + summarization ────────────────────────────────────
  const handleSummarizePdf = async () => {
    if (!pdfFile) return
    resetOutput()
    setIsLoading(true)
    try {
      // FormData is used to send files to the backend
      const formData = new FormData()
      formData.append('file', pdfFile)

      const response = await axios.post(`${BASE_URL}/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSummary(response.data.summary)
      setKeywords(response.data.keywords || [])
    } catch (err) {
      handleError(err)
    } finally {
      setIsLoading(false)
    }
  }

  // ── Unified summarize handler ─────────────────────────────────────────────
  const handleSummarize = () => {
    if (inputMode === 'pdf') {
      handleSummarizePdf()
    } else {
      handleSummarizeText()
    }
  }

  // ── Error handler ─────────────────────────────────────────────────────────
  const handleError = (err) => {
    if (err.response) {
      setError(`Server error: ${err.response.status} — ${err.response.data?.detail || 'Something went wrong'}`)
    } else if (err.request) {
      setError('Could not reach the server. Make sure your FastAPI backend is running on port 8000.')
    } else {
      setError(`Unexpected error: ${err.message}`)
    }
  }

  // ── Determine if summarize button should be enabled ───────────────────────
  const canSummarize = inputMode === 'text'
    ? inputText.trim().length > 0
    : pdfFile !== null

  return (
    <div className="min-h-screen bg-[#f8f7f4] px-4 py-12">
      <div className="mx-auto max-w-2xl">
        <Header />
        <div className="rounded-2xl bg-white border border-stone-200 shadow-sm p-6 flex flex-col gap-6">

          {/* Input mode toggle */}
          <div className="flex rounded-xl overflow-hidden border border-stone-200 w-fit">
            <button
              onClick={() => setInputMode('text')}
              className={`px-5 py-2 text-sm font-medium transition-colors duration-150 ${
                inputMode === 'text'
                  ? 'bg-amber-400 text-stone-800'
                  : 'bg-white text-stone-500 hover:bg-stone-50'
              }`}
            >
              Paste Text
            </button>
            <button
              onClick={() => setInputMode('pdf')}
              className={`px-5 py-2 text-sm font-medium transition-colors duration-150 ${
                inputMode === 'pdf'
                  ? 'bg-amber-400 text-stone-800'
                  : 'bg-white text-stone-500 hover:bg-stone-50'
              }`}
            >
              Upload PDF
            </button>
          </div>

          {/* Input area */}
          <TextInput
            inputMode={inputMode}
            inputText={inputText}
            setInputText={setInputText}
            pdfFile={pdfFile}
            setPdfFile={setPdfFile}
            onSummarize={handleSummarize}
            isLoading={isLoading}
            canSummarize={canSummarize}
          />

          {/* Output: summary + keywords + export */}
          <SummaryCard
            summary={summary}
            keywords={keywords}
            error={error}
            isLoading={isLoading}
          />

        </div>
        <p className="text-center text-xs text-stone-300 mt-6">
          Powered by FastAPI + HuggingFace Transformers
        </p>
      </div>
    </div>
  )
}
