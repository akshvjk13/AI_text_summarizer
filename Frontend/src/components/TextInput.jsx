// src/components/TextInput.jsx
// Handles both input modes:
//   - 'text' mode: large textarea for pasting text
//   - 'pdf'  mode: drag-and-drop / click-to-upload PDF area

export default function TextInput({
  inputMode,
  inputText,
  setInputText,
  pdfFile,
  setPdfFile,
  onSummarize,
  isLoading,
  canSummarize
}) {

  // Handle PDF file selection from the file input
  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file && file.type === 'application/pdf') {
      setPdfFile(file)
    }
  }

  // Handle drag-and-drop PDF upload
  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type === 'application/pdf') {
      setPdfFile(file)
    }
  }

  return (
    <div className="flex flex-col gap-3">

      {/* ── TEXT MODE ─────────────────────────────────────────────────────── */}
      {inputMode === 'text' && (
        <>
          <label className="text-sm font-medium text-stone-600 tracking-wide uppercase">
            Your Text
          </label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste or type a long article, document, or paragraph here..."
            rows={10}
            className="w-full resize-none rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-700 placeholder-stone-300 text-sm leading-relaxed shadow-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent transition duration-200"
          />
          <div className="flex items-center justify-between">
            <span className="text-xs text-stone-400">{inputText.length} characters</span>
            <button
              onClick={onSummarize}
              disabled={!canSummarize || isLoading}
              className="px-6 py-2.5 rounded-xl bg-amber-400 text-stone-800 font-semibold text-sm hover:bg-amber-500 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 shadow-sm"
            >
              {isLoading ? 'Summarizing...' : 'Summarize →'}
            </button>
          </div>
        </>
      )}

      {/* ── PDF MODE ──────────────────────────────────────────────────────── */}
      {inputMode === 'pdf' && (
        <>
          <label className="text-sm font-medium text-stone-600 tracking-wide uppercase">
            Upload PDF
          </label>

          {/* Drop zone */}
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => document.getElementById('pdf-input').click()}
            className="cursor-pointer rounded-xl border-2 border-dashed border-stone-200 bg-stone-50 hover:bg-amber-50 hover:border-amber-300 transition-all duration-200 flex flex-col items-center justify-center py-12 gap-3"
          >
            {/* Upload icon */}
            <div className="text-3xl">📄</div>

            {pdfFile ? (
              // Show selected file name
              <div className="text-center">
                <p className="text-sm font-semibold text-stone-700">{pdfFile.name}</p>
                <p className="text-xs text-stone-400 mt-1">
                  {(pdfFile.size / 1024).toFixed(1)} KB — click to change
                </p>
              </div>
            ) : (
              // Show upload prompt
              <div className="text-center">
                <p className="text-sm font-medium text-stone-600">
                  Click to upload or drag & drop
                </p>
                <p className="text-xs text-stone-400 mt-1">PDF files only</p>
              </div>
            )}

            {/* Hidden file input */}
            <input
              id="pdf-input"
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>

          {/* Summarize button */}
          <div className="flex justify-end">
            <button
              onClick={onSummarize}
              disabled={!canSummarize || isLoading}
              className="px-6 py-2.5 rounded-xl bg-amber-400 text-stone-800 font-semibold text-sm hover:bg-amber-500 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 shadow-sm"
            >
              {isLoading ? 'Processing PDF...' : 'Summarize PDF →'}
            </button>
          </div>
        </>
      )}
    </div>
  )
}
