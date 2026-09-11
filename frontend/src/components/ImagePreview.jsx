function ImagePreview({ fileName, previewUrl, processing, onCount, onRemove }) {
  return (
    <div className="bg-white/80 rounded-3xl p-6 shadow-sm border border-amber-100">
      <h2 className="text-lg font-semibold text-slate-700 mb-4">
        Your uploaded image
      </h2>

      <div className="rounded-2xl overflow-hidden bg-black/5 mb-4 max-h-96 flex justify-center">
        <img
          src={previewUrl}
          alt="Uploaded preview"
          className="max-w-full max-h-96 object-contain"
        />
      </div>

      <p className="text-sm text-slate-600 mb-4 truncate">
        📄 {fileName}
      </p>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={onCount}
          disabled={processing}
          className="flex-1 min-w-40 px-6 py-3 rounded-full bg-amber-600 text-white font-semibold shadow-md hover:bg-amber-700 hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:hover:scale-100 transition-all"
        >
          {processing ? 'Counting... 🍚' : 'Count Rice Grains'}
        </button>
        <button
          type="button"
          onClick={onRemove}
          disabled={processing}
          className="px-6 py-3 rounded-full bg-white border border-slate-300 text-slate-600 font-semibold hover:bg-slate-50 active:scale-95 disabled:opacity-50 transition-all"
        >
          Remove Image
        </button>
      </div>
    </div>
  )
}

export default ImagePreview