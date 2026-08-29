const API_BASE = 'http://localhost:8000/api'

export class ApiError extends Error {
  constructor(code, message, details, status) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.details = details
    this.status = status
  }
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    throw new ApiError(
      'NETWORK_ERROR',
      "Can't reach the server. Check your connection and try again.",
      {},
      0,
    )
  }

  if (response.status === 204) {
    return null
  }

  const body = await response.json().catch(() => null)

  if (!response.ok) {
    const error = body?.error ?? {}
    throw new ApiError(
      error.code ?? 'UNKNOWN_ERROR',
      error.message ?? 'Something went wrong. Please try again.',
      error.details ?? {},
      response.status,
    )
  }

  return body
}

export const api = {
  listTasks() {
    return request('/tasks').then((body) => body.tasks)
  },
  createTask(task) {
    return request('/tasks', { method: 'POST', body: JSON.stringify(task) })
  },
  updateTask(id, patch) {
    return request(`/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(patch) })
  },
  deleteTask(id) {
    return request(`/tasks/${id}`, { method: 'DELETE' })
  },
}
