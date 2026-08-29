import { useDroppable } from '@dnd-kit/core'
import TaskCard from './TaskCard.jsx'

function sortForDisplay(tasks) {
  const scheduled = tasks
    .filter((t) => t.scheduled_at)
    .sort((a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at))
  const unscheduled = tasks.filter((t) => !t.scheduled_at)
  return { scheduled, unscheduled }
}

export default function TaskColumn({ status, label, tasks, onEdit, onDelete }) {
  const { scheduled, unscheduled } = sortForDisplay(tasks)

  // Dropping directly on a task (TaskCard's own droppable) targets that task's
  // exact time slot; dropping in this column's general "scheduled" area instead
  // assigns the next available time (FR-006). Dropping in the "unscheduled" area
  // clears the schedule entirely (Edge Cases).
  const { setNodeRef: setScheduleRef, isOver: isOverSchedule } = useDroppable({
    id: `column-schedule:${status}`,
  })
  const { setNodeRef: setUnscheduledRef, isOver: isOverUnscheduled } = useDroppable({
    id: `column-unscheduled:${status}`,
  })

  return (
    <section aria-label={label} data-status={status}>
      <h2>{label}</h2>
      <div
        ref={setScheduleRef}
        className="drop-zone"
        data-over={isOverSchedule ? 'true' : undefined}
      >
        {scheduled.map((task) => (
          <TaskCard key={task.id} task={task} onEdit={onEdit} onDelete={onDelete} />
        ))}
        {scheduled.length === 0 && <p className="drop-zone-hint">Drop here to schedule</p>}
      </div>
      <h3>Unscheduled</h3>
      <div
        ref={setUnscheduledRef}
        className="drop-zone"
        data-over={isOverUnscheduled ? 'true' : undefined}
      >
        {unscheduled.map((task) => (
          <TaskCard key={task.id} task={task} onEdit={onEdit} onDelete={onDelete} />
        ))}
        {unscheduled.length === 0 && <p className="drop-zone-hint">Drop here to unschedule</p>}
      </div>
    </section>
  )
}
