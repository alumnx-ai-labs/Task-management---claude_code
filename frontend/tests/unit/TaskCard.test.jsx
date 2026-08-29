import { DndContext } from '@dnd-kit/core'
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import TaskCard from '../../src/components/TaskCard.jsx'

function renderCard(task, props = {}) {
  return render(
    <DndContext>
      <TaskCard task={task} {...props} />
    </DndContext>,
  )
}

describe('TaskCard', () => {
  it('shows "Unscheduled" when the task has no scheduled_at', () => {
    renderCard({ id: '1', title: 'Backlog item', status: 'todo', scheduled_at: null })

    expect(screen.getByTestId('scheduled-at')).toHaveTextContent('Unscheduled')
  })

  it('truncates a long description with a Show more toggle', () => {
    const longDescription = 'x'.repeat(200)
    renderCard({
      id: '1',
      title: 'Task with notes',
      status: 'todo',
      scheduled_at: null,
      description: longDescription,
    })

    expect(screen.getByText(/x+…/)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Show more' }))

    expect(screen.getByText(longDescription)).toBeInTheDocument()
  })
})
