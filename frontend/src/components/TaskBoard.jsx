import { DndContext, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import TaskColumn from './TaskColumn.jsx'
import { STATUSES } from './TaskForm.jsx'

export default function TaskBoard({ tasks, onEdit, onDelete, onDragEnd }) {
  // A small activation distance keeps ordinary clicks (Edit/Delete/Show more)
  // from being swallowed as drag starts.
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
  )

  return (
    <DndContext sensors={sensors} onDragEnd={onDragEnd}>
      <div className="task-board">
        {STATUSES.map(({ value, label }) => (
          <TaskColumn
            key={value}
            status={value}
            label={label}
            tasks={tasks.filter((t) => t.status === value)}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </div>
    </DndContext>
  )
}
