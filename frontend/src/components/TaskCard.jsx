import { useState } from 'react'
import { useDraggable, useDroppable } from '@dnd-kit/core'

const DESCRIPTION_PREVIEW_LENGTH = 120

function formatScheduledAt(isoString) {
  if (!isoString) return 'Unscheduled'
  return new Date(isoString).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export default function TaskCard({ task, onEdit, onDelete }) {
  const [expanded, setExpanded] = useState(false)
  const description = task.description ?? ''
  const isLong = description.length > DESCRIPTION_PREVIEW_LENGTH
  const shownDescription =
    isLong && !expanded ? `${description.slice(0, DESCRIPTION_PREVIEW_LENGTH)}…` : description

  // A card is both a drag source (moving this task) and a drop target
  // (dropping another task onto it means "take this task's exact time slot",
  // which the backend will accept only if it's actually free — FR-006, FR-007).
  const { attributes, listeners, setNodeRef: setDragRef, transform, isDragging } = useDraggable({
    id: task.id,
  })
  const { setNodeRef: setDropRef, isOver } = useDroppable({ id: `card:${task.id}` })

  const setRefs = (node) => {
    setDragRef(node)
    setDropRef(node)
  }

  const style = {
    transform: transform ? `translate(${transform.x}px, ${transform.y}px)` : undefined,
    opacity: isDragging ? 0.5 : undefined,
    outline: isOver ? '2px dashed currentColor' : undefined,
  }

  return (
    <article ref={setRefs} style={style} data-task-id={task.id} {...attributes} {...listeners}>
      <h3>{task.title}</h3>
      <p data-testid="scheduled-at">{formatScheduledAt(task.scheduled_at)}</p>
      {description && (
        <p>
          {shownDescription}{' '}
          {isLong && (
            <button type="button" onClick={() => setExpanded((v) => !v)}>
              {expanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </p>
      )}
      <div>
        {onEdit && (
          <button type="button" onClick={() => onEdit(task)}>
            Edit
          </button>
        )}
        {onDelete && (
          <button
            type="button"
            onClick={() => {
              if (window.confirm(`Delete "${task.title}"? This cannot be undone.`)) {
                onDelete(task)
              }
            }}
          >
            Delete
          </button>
        )}
      </div>
    </article>
  )
}
