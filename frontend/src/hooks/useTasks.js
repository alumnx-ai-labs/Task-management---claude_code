import { useCallback, useEffect, useState } from 'react'
import { api } from '../services/api.js'

export default function useTasks() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)

  const reload = useCallback(async () => {
    const loaded = await api.listTasks()
    setTasks(loaded)
    return loaded
  }, [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    reload()
      .catch((err) => {
        if (!cancelled) setLoadError(err)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [reload])

  const createTask = useCallback(async (data) => {
    const created = await api.createTask(data)
    setTasks((prev) => [...prev, created])
    return created
  }, [])

  const updateTask = useCallback(async (id, patch) => {
    const updated = await api.updateTask(id, patch)
    setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)))
    return updated
  }, [])

  const deleteTask = useCallback(async (id) => {
    await api.deleteTask(id)
    setTasks((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return { tasks, setTasks, loading, loadError, reload, createTask, updateTask, deleteTask }
}
