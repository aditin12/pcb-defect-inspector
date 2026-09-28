import { useRef, useState } from 'react'

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/jpg', 'image/bmp']

export default function UploadZone({ onFileSelected }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  function handleFiles(fileList) {
    const file = fileList?.[0]
    if (!file) return
    if (!ACCEPTED_TYPES.includes(file.type)) {
      onFileSelected(null, 'Please upload a JPG, PNG, or BMP image of a PCB.')
      return
    }
    onFileSelected(file, null)
  }

  return (
    <div
      className={`dropzone ${dragging ? 'dragging' : ''}`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files) }}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter') inputRef.current?.click() }}
    >
      <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <circle cx="8" cy="8" r="1.2" fill="currentColor" />
        <circle cx="16" cy="8" r="1.2" fill="currentColor" />
        <circle cx="8" cy="16" r="1.2" fill="currentColor" />
        <path d="M8 9.2V14.8M9.2 16H14.8M16 9.2V14.8" strokeLinecap="round" />
      </svg>
      <p className="dz-title">Drop a PCB image, or click to browse</p>
      <p className="dz-sub">JPG, PNG, BMP · up to 10MB</p>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/bmp"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  )
}
