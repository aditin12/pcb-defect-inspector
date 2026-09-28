import { useEffect, useState } from 'react'
import UploadZone from './components/UploadZone.jsx'
import PreviewPanel from './components/PreviewPanel.jsx'
import ResultsPanel from './components/ResultsPanel.jsx'
import { checkHealth, inspectBoard } from './api.js'

export default function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [health, setHealth] = useState(null)

  useEffect(() => {
    checkHealth().then(setHealth).catch(() => setHealth({ status: 'unreachable', model_loaded: false }))
  }, [])

  function handleFileSelected(selectedFile, err) {
    if (err) { setError(err); return }
    setError(null)
    setResult(null)
    setFile(selectedFile)
    setPreviewUrl(URL.createObjectURL(selectedFile))
  }

  function handleReset() {
    setFile(null); setPreviewUrl(null); setResult(null); setError(null)
  }

  async function handleAnalyze() {
    setAnalyzing(true)
    setError(null)
    try {
      const data = await inspectBoard(file)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setAnalyzing(false)
    }
  }

  const isOnline = health?.model_loaded && health?.rag_index_loaded

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark" />
          <h1>PCB Inspector</h1>
          <span className="brand-sub">/ CV → ML → RAG defect analysis</span>
        </div>
        <div className={`model-chip ${health ? (isOnline ? 'online' : 'offline') : ''}`}>
          <span className="dot" />
          {health ? (isOnline ? 'pipeline online' : 'pipeline unavailable') : 'checking…'}
        </div>
      </header>

      <div className="workbench">
        <div className="panel">
          <p className="panel-label">INPUT BOARD IMAGE</p>
          {!file ? (
            <UploadZone onFileSelected={handleFileSelected} />
          ) : (
            <PreviewPanel previewUrl={previewUrl} file={file} analyzing={analyzing} onAnalyze={handleAnalyze} onReset={handleReset} />
          )}
          {error && <div className="error-banner">{error}</div>}
        </div>

        <div className="panel">
          <p className="panel-label">INSPECTION RESULTS</p>
          <ResultsPanel result={result} />
        </div>
      </div>

      <p className="footer-note">
        YOLOv8 defect detection · rule-based severity grading · RAG explanations grounded in a PCB defect knowledge base
      </p>
    </div>
  )
}
