import { useState } from 'react'
import ErrorBanner from '../components/ErrorBanner.jsx'
import TaskBoard from '../components/TaskBoard.jsx'
import TaskForm from '../components/TaskForm.jsx'
import useDragAndDrop from '../hooks/useDragAndDrop.js'
import useTasks from '../hooks/useTasks.js'

export default function BoardPage() {
  const { tasks, setTasks, loading, loadError, createTask, updateTask, deleteTask } = useTasks()
  const [error, setError] = useState(null)
  const displayedError = error ?? loadError
  const [editingTask, setEditingTask] = useState(null)
  const { handleDragEnd } = useDragAndDrop({ tasks, setTasks, onError: setError })

  async function handleCreate(data) {
    setError(null)
    try {
      await createTask(data)
    } catch (err) {
      setError(err)
    }
  }

  async function handleUpdate(data) {
    setError(null)
    try {
      await updateTask(editingTask.id, data)
      setEditingTask(null)
    } catch (err) {
      setError(err)
    }
  }

  async function handleDelete(task) {
    setError(null)
    try {
      await deleteTask(task.id)
    } catch (err) {
      setError(err)
    }
  }

  return (
    <main>
      <h1>Task Board</h1>
      <ErrorBanner error={displayedError} onDismiss={() => setError(null)} />
      {editingTask ? (
        <TaskForm
          key={editingTask.id}
          initialValues={editingTask}
          submitLabel="Save Changes"
          onSubmit={handleUpdate}
          onCancel={() => setEditingTask(null)}
        />
      ) : (
        <TaskForm onSubmit={handleCreate} />
      )}
      {loading ? (
        <p>Loading tasks…</p>
      ) : (
        <TaskBoard
          tasks={tasks}
          onEdit={setEditingTask}
          onDelete={handleDelete}
          onDragEnd={handleDragEnd}
        />
      )}
    </main>
  )
}
