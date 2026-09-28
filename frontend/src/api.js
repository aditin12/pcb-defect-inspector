const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) throw new Error('Health check failed')
  return res.json()
}

export async function inspectBoard(file) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE}/inspect?explain=true`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    let detail = 'Inspection failed. Please try again.'
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {}
    throw new Error(detail)
  }
  return res.json()
}

export async function askAboutBoard(question, defectTypes) {
  const res = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, defect_types: defectTypes }),
  })
  if (!res.ok) {
    let detail = 'Could not answer that question.'
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {}
    throw new Error(detail)
  }
  return res.json()
}
