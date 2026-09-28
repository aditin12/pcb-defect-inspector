export default function PreviewPanel({ previewUrl, file, analyzing, onAnalyze, onReset }) {
  return (
    <>
      <div className="preview-wrap">
        <img src={previewUrl} alt="Uploaded PCB" />
        {analyzing && (
          <div className="scan-overlay-wrap"><div className="scan-overlay" /></div>
        )}
      </div>
      <div className="preview-meta">
        <span>{file.name}</span>
        <span>{(file.size / 1024).toFixed(0)} KB</span>
      </div>
      <button className="btn btn-primary" onClick={onAnalyze} disabled={analyzing}>
        {analyzing ? 'Inspecting…' : 'Run Inspection'}
      </button>
      {analyzing && <p className="spin-note">Detecting defects → grading severity → retrieving explanations…</p>}
      <button className="btn btn-ghost" style={{ width: '100%', marginTop: 10 }} onClick={onReset} disabled={analyzing}>
        Upload a different board
      </button>
    </>
  )
}
