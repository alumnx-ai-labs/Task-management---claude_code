import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import TaskForm from '../../src/components/TaskForm.jsx'

describe('TaskForm', () => {
  it('disables submit while the title is blank', () => {
    render(<TaskForm onSubmit={vi.fn()} />)

    expect(screen.getByRole('button', { name: 'Create Task' })).toBeDisabled()
  })

  it('enables submit once a title is entered and calls onSubmit with trimmed values', () => {
    const onSubmit = vi.fn()
    render(<TaskForm onSubmit={onSubmit} />)

    fireEvent.change(screen.getByLabelText('Title'), { target: { value: '  New task  ' } })
    const button = screen.getByRole('button', { name: 'Create Task' })
    expect(button).not.toBeDisabled()

    fireEvent.click(button)

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'New task', status: 'todo' }),
    )
  })

  it('stays disabled for a whitespace-only title', () => {
    render(<TaskForm onSubmit={vi.fn()} />)

    fireEvent.change(screen.getByLabelText('Title'), { target: { value: '   ' } })

    expect(screen.getByRole('button', { name: 'Create Task' })).toBeDisabled()
  })
})
