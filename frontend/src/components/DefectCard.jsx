import { useState } from 'react'

function formatName(name) {
  return name.replace(/_/g, ' ')
}

export default function DefectCard({ detection }) {
  const [open, setOpen] = useState(false)
  const { class_name, confidence, severity, explanation } = detection

  return (
    <div className="defect-card">
      <div className="defect-card-head" onClick={() => setOpen(!open)}>
        <div className="defect-name-row">
          <span className={`sev-dot ${severity.level}`} />
          <span className="defect-name">{formatName(class_name)}</span>
        </div>
        <div className="defect-meta">
          <span>{Math.round(confidence * 100)}% conf</span>
          <span style={{ textTransform: 'uppercase' }}>{severity.level}</span>
          <span>{open ? '−' : '+'}</span>
        </div>
      </div>
      {open && (
        <div className="defect-card-body">
          {explanation ? (
            <>
              <p className="explanation-text">{explanation.explanation}</p>
              {explanation.sources?.length > 0 && (
                <p className="sources">
                  SOURCES: {explanation.sources.map((s) => `${s.source_doc} / ${s.section}`).join('  ·  ')}
                </p>
              )}
              <span className="backend-tag">generated via {explanation.backend_used}</span>
            </>
          ) : (
            <p>No explanation available for this detection.</p>
          )}
        </div>
      )}
    </div>
  )
}
