import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import ErrorBanner from '../../src/components/ErrorBanner.jsx'

describe('ErrorBanner', () => {
  it('renders nothing when there is no error', () => {
    const { container } = render(<ErrorBanner error={null} />)

    expect(container).toBeEmptyDOMElement()
  })

  it('renders the error message when an error is present', () => {
    render(<ErrorBanner error={{ message: 'A task titled "Team Sync" already exists.' }} />)

    expect(screen.getByRole('alert')).toHaveTextContent('already exists')
  })
})
