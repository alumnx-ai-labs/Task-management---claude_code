import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import useDragAndDrop from '../../src/hooks/useDragAndDrop.js'
import { api, ApiError } from '../../src/services/api.js'

vi.mock('../../src/services/api.js', () => ({
  api: { updateTask: vi.fn() },
  ApiError: class ApiError extends Error {
    constructor(code, message) {
      super(message)
      this.code = code
    }
  },
}))

function setup(initialTasks) {
  let tasks = initialTasks
  const setTasks = vi.fn((updater) => {
    tasks = typeof updater === 'function' ? updater(tasks) : updater
  })
  const onError = vi.fn()
  const { result, rerender } = renderHook(
    ({ currentTasks }) => useDragAndDrop({ tasks: currentTasks, setTasks, onError }),
    { initialProps: { currentTasks: tasks } },
  )
  return { result, rerender, setTasks, onError, getTasks: () => tasks }
}

describe('useDragAndDrop', () => {
  beforeEach(() => {
    api.updateTask.mockReset()
  })

  it('optimistically updates and then reconciles with the server response on success', async () => {
    const task = { id: 't1', title: 'A', status: 'todo', scheduled_at: null }
    const serverResult = { ...task, status: 'in_progress' }
    api.updateTask.mockResolvedValue(serverResult)
    const { result, setTasks } = setup([task])

    await act(async () => {
      result.current.handleDragEnd({
        active: { id: 't1' },
        over: { id: 'column-schedule:in_progress' },
      })
      await Promise.resolve()
      await Promise.resolve()
    })

    // First call: optimistic update. Second call: reconciled with server response.
    expect(setTasks).toHaveBeenCalledTimes(2)
  })

  it('rolls back the optimistic update and reports the error when the backend rejects it', async () => {
    const taskA = { id: 't1', title: 'A', status: 'todo', scheduled_at: '2026-09-03T14:30:00Z' }
    const taskB = { id: 't2', title: 'B', status: 'todo', scheduled_at: '2026-09-04T09:00:00Z' }
    api.updateTask.mockRejectedValue(new ApiError('SCHEDULING_CONFLICT', 'That time is taken.'))
    const { result, onError, getTasks } = setup([taskA, taskB])

    await act(async () => {
      result.current.handleDragEnd({ active: { id: 't2' }, over: { id: 'card:t1' } })
      await Promise.resolve()
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(onError).toHaveBeenCalledTimes(1)
    expect(onError.mock.calls[0][0].message).toBe('That time is taken.')
    // Rolled back to the original array reference passed into the hook.
    expect(getTasks()).toEqual([taskA, taskB])
  })

  it('ignores a drop outside any valid target', async () => {
    const task = { id: 't1', title: 'A', status: 'todo', scheduled_at: null }
    const { result, setTasks } = setup([task])

    result.current.handleDragEnd({ active: { id: 't1' }, over: null })

    expect(setTasks).not.toHaveBeenCalled()
    expect(api.updateTask).not.toHaveBeenCalled()
  })
})
