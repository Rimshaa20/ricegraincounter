const TIPS = [
  'Place rice grains on a plain contrasting background.',
  'Avoid heavy overlap between grains.',
  'Use good lighting.',
  'Take the photo from directly above.',
  'Keep the entire rice sample visible.',
  'Use a high-resolution image.',
]

function TipsList() {
  return (
    <section className="mt-8 bg-white/70 rounded-3xl p-6 border border-amber-100">
      <h2 className="text-base font-semibold text-slate-700 mb-3">
        For better results:
      </h2>
      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {TIPS.map((tip) => (
          <li key={tip} className="flex items-start gap-2 text-sm text-slate-600">
            <span className="text-amber-500 mt-0.5">✦</span>
            {tip}
          </li>
        ))}
      </ul>
    </section>
  )
}

export default TipsList