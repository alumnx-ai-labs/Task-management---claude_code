export default function ErrorBanner({ error, onDismiss }) {
  if (!error) return null

  return (
    <div role="alert">
      <p>{error.message}</p>
      {onDismiss && (
        <button type="button" onClick={onDismiss}>
          Dismiss
        </button>
      )}
    </div>
  )
}
