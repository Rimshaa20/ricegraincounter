function ResultPanel({ result, originalUrl, onReset }) {
  const count = result.total_count

  return (
    <div className="space-y-6">
      {/* Count headline */}
      <div className="bg-white/80 rounded-3xl p-8 text-center shadow-sm border border-amber-100 animate-fade-in-up">
        <h2 className="text-lg font-semibold text-slate-600">
          Rice Grains Counted
        </h2>
        <div className="mt-2 text-7xl sm:text-8xl font-extrabold text-amber-700 tracking-tight">
          {count}
        </div>
        <p className="mt-3 text-base sm:text-lg text-slate-500">
          {count} rice grain{count === 1 ? '' : 's'} detected 🍚
        </p>
      </div>

      {/* Side-by-side images */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-white/80 rounded-3xl p-4 shadow-sm border border-amber-100">
          <h3 className="text-sm font-semibold text-slate-500 mb-2">
            Original image
          </h3>
          <img
            src={originalUrl}
            alt="Original uploaded rice"
            className="w-full rounded-2xl object-contain max-h-72"
          />
        </div>
        <div className="bg-white/80 rounded-3xl p-4 shadow-sm border border-amber-100">
          <h3 className="text-sm font-semibold text-slate-500 mb-2">
            Processed — detected grains numbered
          </h3>
          <img
            src={`data:image/jpeg;base64,${result.annotated_image}`}
            alt="Annotated rice grains"
            className="w-full rounded-2xl object-contain max-h-72 bg-black/5"
          />
        </div>
      </div>

      <div className="text-center">
        <button
          type="button"
          onClick={onReset}
          className="px-8 py-3 rounded-full bg-amber-600 text-white font-semibold shadow-md hover:bg-amber-700 hover:scale-[1.02] active:scale-95 transition-all"
        >
          Count Another Image
        </button>
      </div>
    </div>
  )
}

export default ResultPanel