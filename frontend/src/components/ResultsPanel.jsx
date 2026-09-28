import DefectCard from './DefectCard.jsx'
import AskPanel from './AskPanel.jsx'

function EmptyState() {
  return (
    <div className="results-empty">
      <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.3">
        <circle cx="11" cy="11" r="7" />
        <path d="M21 21l-4.35-4.35" strokeLinecap="round" />
      </svg>
      <p>Upload a PCB image and run an inspection to see detected defects, severity grading, and grounded explanations here.</p>
    </div>
  )
}

const VERDICT_COPY = {
  high: { title: 'High-severity defects found', sub: 'Manual review recommended before proceeding.' },
  medium: { title: 'Medium-severity defects found', sub: 'Review flagged items before sign-off.' },
  low: { title: 'Only low-severity defects found', sub: 'Board likely acceptable; findings logged for monitoring.' },
  pass: { title: 'No defects detected', sub: 'No issues found at the current confidence threshold.' },
}

export default function ResultsPanel({ result }) {
  if (!result) return <EmptyState />

  const { detections, board_summary, annotated_image_base64, inference_time_ms, model_name } = result
  const verdict = VERDICT_COPY[board_summary.overall_level] || VERDICT_COPY.pass
  const defectTypes = detections.map((d) => d.class_name)

  return (
    <div>
      <div className={`verdict-banner ${board_summary.overall_level}`}>
        <div>
          <p className="verdict-title">{verdict.title}</p>
          <p className="verdict-sub">{verdict.sub}</p>
        </div>
        <div className="verdict-counts">
          <span>HIGH <b>{board_summary.counts.high}</b></span>
          <span>MED <b>{board_summary.counts.medium}</b></span>
          <span>LOW <b>{board_summary.counts.low}</b></span>
        </div>
      </div>

      <div className="preview-wrap" style={{ marginBottom: 20 }}>
        <img src={`data:image/png;base64,${annotated_image_base64}`} alt="Annotated PCB with detected defects" />
      </div>

      {detections.length > 0 && (
        <>
          <p className="panel-label">DETECTED DEFECTS ({detections.length})</p>
          <div className="defect-list">
            {detections.map((d, i) => (
              <DefectCard key={i} detection={d} />
            ))}
          </div>
        </>
      )}

      {detections.length > 0 && <AskPanel defectTypes={defectTypes} />}

      <div className="preview-meta" style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--board-700)' }}>
        <span>MODEL {model_name}</span>
        <span>INFERENCE {inference_time_ms.toFixed(0)}ms</span>
      </div>
    </div>
  )
}
