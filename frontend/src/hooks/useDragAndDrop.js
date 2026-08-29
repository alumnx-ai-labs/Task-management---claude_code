import { useCallback } from 'react'
import { api } from '../services/api.js'

function resolvePatchFromDropTarget(overId, tasks) {
  if (overId.startsWith('card:')) {
    const targetId = overId.slice('card:'.length)
    const target = tasks.find((t) => t.id === targetId)
    if (!target) return null
    return { status: target.status, scheduled_at: target.scheduled_at }
  }
  if (overId.startsWith('column-unscheduled:')) {
    return { status: overId.slice('column-unscheduled:'.length), scheduled_at: null }
  }
  if (overId.startsWith('column-schedule:')) {
    const now = new Date()
    now.setSeconds(0, 0)
    return { status: overId.slice('column-schedule:'.length), scheduled_at: now.toISOString() }
  }
  return null
}

export default function useDragAndDrop({ tasks, setTasks, onError }) {
  const handleDragEnd = useCallback(
    (event) => {
      const { active, over } = event
      // Dropped outside any valid target — ignored, task stays put (FR-007).
      if (!over) return

      const taskId = active.id
      const task = tasks.find((t) => t.id === taskId)
      if (!task) return

      const patch = resolvePatchFromDropTarget(String(over.id), tasks)
      if (!patch) return
      if (patch.status === task.status && patch.scheduled_at === task.scheduled_at) return

      const previousTasks = tasks
      setTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, ...patch } : t)))

      api
        .updateTask(taskId, patch)
        .then((updated) => {
          setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)))
        })
        .catch((error) => {
          setTasks(previousTasks)
          onError(error)
        })
    },
    [tasks, setTasks, onError],
  )

  return { handleDragEnd }
}
