function ErrorBanner({ message, onDismiss }) {
  return (
    <div
      role="alert"
      className="mb-6 flex items-start gap-3 bg-red-50 border border-red-200 text-red-700 rounded-2xl px-4 py-3"
    >
      <span className="text-lg leading-none mt-0.5">⚠️</span>
      <p className="flex-1 text-sm">{message}</p>
      <button
        type="button"
        onClick={onDismiss}
        aria-label="Dismiss error"
        className="text-red-400 hover:text-red-600 text-lg leading-none transition-colors"
      >
        ×
      </button>
    </div>
  )
}

export default ErrorBanner