import { useRef, useState } from 'react'

function UploadZone({ onFileSelect }) {
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const dropped = e.dataTransfer.files && e.dataTransfer.files[0]
    if (dropped) onFileSelect(dropped)
  }

  const handleChange = (e) => {
    const selected = e.target.files && e.target.files[0]
    if (selected) onFileSelect(selected)
    // Reset input value so the same file can be chosen again
    e.target.value = ''
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => inputRef.current && inputRef.current.click()}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          inputRef.current && inputRef.current.click()
        }
      }}
      onDragOver={(e) => {
        e.preventDefault()
        setDragOver(true)
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      className={`cursor-pointer border-2 border-dashed rounded-3xl p-10 sm:p-16 text-center transition-all duration-200 bg-white/80 ${
        dragOver
          ? 'border-amber-500 bg-amber-50 scale-[1.02]'
          : 'border-amber-200 hover:border-amber-400 hover:bg-amber-50/50'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/jpg"
        onChange={handleChange}
        className="hidden"
      />

      <div className="flex justify-center mb-4">
        <span className="text-5xl animate-bounce select-none">🍚</span>
      </div>

      <p className="text-lg font-semibold text-slate-700">
        Drag & drop your rice photo here
      </p>
      <p className="text-sm text-slate-500 mt-1">or</p>
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation()
          inputRef.current && inputRef.current.click()
        }}
        className="mt-4 px-6 py-3 rounded-full bg-amber-600 text-white font-semibold shadow-md hover:bg-amber-700 hover:scale-105 active:scale-95 transition-all"
      >
        Upload Rice Image
      </button>

      <p className="mt-6 text-xs text-slate-400">
        Supported formats: JPG, JPEG, PNG • Max 10 MB
      </p>
    </div>
  )
}

export default UploadZone