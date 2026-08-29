import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import TaskBoard from '../../src/components/TaskBoard.jsx'

describe('TaskBoard', () => {
  it('renders four columns in order: backlog, todo, in_progress, done', () => {
    render(<TaskBoard tasks={[]} onDragEnd={() => {}} />)

    const sections = screen.getAllByRole('region')
    const statuses = sections.map((s) => s.getAttribute('data-status'))

    expect(statuses).toEqual(['backlog', 'todo', 'in_progress', 'done'])
  })

  it('shows a backlog task in the Backlog column', () => {
    const backlogTask = {
      id: 't1',
      title: 'Someday idea',
      status: 'backlog',
      scheduled_at: null,
    }
    render(<TaskBoard tasks={[backlogTask]} onDragEnd={() => {}} />)

    const backlogSection = screen.getByLabelText('Backlog')
    expect(backlogSection).toHaveTextContent('Someday idea')
  })
})
