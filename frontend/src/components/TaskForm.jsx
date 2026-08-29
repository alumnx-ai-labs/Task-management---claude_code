import { useState } from 'react'

const STATUSES = [
  { value: 'todo', label: 'To Do' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' },
]

function toDatetimeLocal(isoString) {
  if (!isoString) return ''
  const date = new Date(isoString)
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(
    date.getHours(),
  )}:${pad(date.getMinutes())}`
}

export default function TaskForm({ initialValues, submitLabel = 'Create Task', onSubmit, onCancel }) {
  const [title, setTitle] = useState(initialValues?.title ?? '')
  const [description, setDescription] = useState(initialValues?.description ?? '')
  const [scheduledAt, setScheduledAt] = useState(toDatetimeLocal(initialValues?.scheduled_at))
  const [status, setStatus] = useState(initialValues?.status ?? 'todo')

  const isTitleBlank = title.trim().length === 0

  function handleSubmit(event) {
    event.preventDefault()
    if (isTitleBlank) return

    onSubmit({
      title: title.trim(),
      description: description.trim() || null,
      scheduled_at: scheduledAt ? new Date(scheduledAt).toISOString() : null,
      status,
    })
  }

  return (
    <form onSubmit={handleSubmit} aria-label={submitLabel}>
      <div>
        <label htmlFor="task-title">Title</label>
        <input
          id="task-title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="task-description">Description</label>
        <textarea
          id="task-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="task-scheduled-at">Scheduled date &amp; time</label>
        <input
          id="task-scheduled-at"
          type="datetime-local"
          value={scheduledAt}
          onChange={(e) => setScheduledAt(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="task-status">Status</label>
        <select id="task-status" value={status} onChange={(e) => setStatus(e.target.value)}>
          {STATUSES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>
      <button type="submit" disabled={isTitleBlank}>
        {submitLabel}
      </button>
      {onCancel && (
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
      )}
    </form>
  )
}

export { STATUSES }
