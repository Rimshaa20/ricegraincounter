import { useCallback, useRef, useState } from 'react'
import UploadZone from './components/UploadZone'
import ImagePreview from './components/ImagePreview'
import ResultPanel from './components/ResultPanel'
import TipsList from './components/TipsList'
import ErrorBanner from './components/ErrorBanner'

const IMAGE_URL = '/count-rice'

function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [fileName, setFileName] = useState('')
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Keep a ref to the preview URL so we can revoke it when replaced
  const previewUrlRef = useRef(null)

  const VALID_TYPES = ['image/jpeg', 'image/png', 'image/jpg']
  const MAX_SIZE = 10 * 1024 * 1024 // 10 MB

  const selectFile = useCallback((selected) => {
    if (!selected) return

    // Client-side validation
    if (!VALID_TYPES.includes(selected.type)) {
      setError('Invalid file format. Please upload a JPG, JPEG or PNG image.')
      removeImage()
      return
    }
    if (selected.size > MAX_SIZE) {
      setError(`File too large (${(selected.size / (1024 * 1024)).toFixed(1)} MB). Maximum size is 10 MB.`)
      removeImage()
      return
    }
    if (selected.size === 0) {
      setError('The selected file is empty. Please choose another image.')
      removeImage()
      return
    }

    // Revoke the old preview URL before creating a new one
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current)
    }

    const url = URL.createObjectURL(selected)
    previewUrlRef.current = url

    setFile(selected)
    setPreviewUrl(url)
    setFileName(selected.name)
    setError(null)
    setResult(null)
  }, [VALID_TYPES, MAX_SIZE])

  const removeImage = useCallback(() => {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current)
      previewUrlRef.current = null
    }
    setFile(null)
    setPreviewUrl(null)
    setFileName('')
    setResult(null)
    setError(null)
  }, [])

  const resetAll = useCallback(() => {
    removeImage()
    setProcessing(false)
  }, [removeImage])

  const countGrains = useCallback(async () => {
    if (!file) {
      setError('No image selected. Please upload an image first.')
      return
    }

    setProcessing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch("https://ricegraincounter.onrender.com/count-rice", {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || `Server error (status ${response.status})`)
      }

      setResult(data)
    } catch (err) {
      const message = err.message.includes('Failed to fetch')
        ? 'Could not reach the backend server. Make sure it is running (cd backend && python main.py).'
        : err.message
      setError(message)
    } finally {
      setProcessing(false)
    }
  }, [file])

  return (
    <div className="min-h-screen bg-[#faf6ef] text-slate-800">
      <div className="max-w-3xl mx-auto px-4 py-10 sm:py-14">
        {/* Header */}
        <header className="text-center mb-10">
          <h1 className="text-4xl sm:text-5xl font-bold text-amber-700">
            Rice Grain Counter 🍚
          </h1>
          <p className="mt-3 text-base sm:text-lg text-slate-500">
            Upload a photo and discover how many rice grains are hiding in it!
          </p>
        </header>

        {error && (
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
        )}

        {!result && (
          <>
            {!file ? (
              <UploadZone onFileSelect={selectFile} />
            ) : (
              <ImagePreview
                fileName={fileName}
                previewUrl={previewUrl}
                processing={processing}
                onCount={countGrains}
                onRemove={removeImage}
              />
            )}
            <TipsList />
          </>
        )}

        {result && (
          <ResultPanel
            result={result}
            originalUrl={previewUrl}
            onReset={resetAll}
          />
        )}

        <footer className="mt-14 text-center text-xs text-slate-400">
          Counting accuracy depends on image quality, lighting, grain overlap,
          background, and whether individual grains are clearly visible.
        </footer>
      </div>
    </div>
  )
}

export default App
