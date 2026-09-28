import { useState } from 'react'
import { askAboutBoard } from '../api.js'

export default function AskPanel({ defectTypes }) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [asking, setAsking] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!question.trim()) return
    setAsking(true)
    setError(null)
    try {
      const result = await askAboutBoard(question, defectTypes)
      setAnswer(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setAsking(false)
    }
  }

  return (
    <div className="ask-panel">
      <p className="panel-label" style={{ marginBottom: 0 }}>ASK ABOUT THIS BOARD</p>
      <form className="ask-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="e.g. is this board safe to assemble?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit" disabled={asking}>{asking ? '…' : 'Ask'}</button>
      </form>
      {error && <div className="error-banner">{error}</div>}
      {answer && (
        <div className="ask-answer">
          {answer.answer}
        </div>
      )}
    </div>
  )
}
