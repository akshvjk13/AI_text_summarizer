// src/components/Header.jsx — no changes needed from v1
export default function Header() {
  return (
    <header className="text-center mb-10">
      <h1 className="text-4xl font-bold text-stone-800 tracking-tight">
        AI Text Summarizer
      </h1>
      <p className="mt-2 text-stone-500 text-base">
        Paste text or upload a PDF to get an instant AI summary.
      </p>
      <div className="mx-auto mt-4 h-1 w-16 rounded-full bg-amber-400" />
    </header>
  )
}
