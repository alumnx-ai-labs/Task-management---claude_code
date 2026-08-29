# Phase 0 Research: Backlog Status Column

No open technical questions. This feature makes no new technology or
architecture decision — it reuses every decision already made and validated in
`../001-task-management/research.md`. The two points below are the only
"decisions" specific to this feature, and both have a single, low-risk answer.

## 1. Where the new status value is enforced

- **Decision**: The backend's Pydantic `Status` `Literal` type
  (`backend/src/schemas/task.py`) remains the single source of truth for which
  status values are valid, per Constitution Principle IV/V. The frontend's
  `STATUSES` list is a display/UI concern only (order + form options), not a
  validation authority — it already isn't one today for `todo`/`in_progress`/`done`.
- **Rationale**: Consistent with how the existing three statuses are already
  enforced; adding a fourth value doesn't change where validation authority
  lives.
- **Alternatives considered**: Enforcing status values via a database `CHECK`
  constraint — rejected as unnecessary; the column is already a plain string
  and Principle VII (Simplicity) doesn't call for adding a DB-level constraint
  the application layer already provides.

## 2. Visual distinction for the new column

- **Decision**: Give the Backlog column its own accent color (a fourth color,
  distinct from the existing To Do/In Progress/Done colors already defined in
  `frontend/src/index.css`), rather than reusing the To Do color.
- **Rationale**: The existing CSS already gives each status a distinct
  top-border accent color; leaving Backlog unstyled would make it silently
  inherit the To Do color and look like a visual duplicate, undermining "a
  clear visual task board" from the original 001 feature intent.
- **Alternatives considered**: Reusing an existing color (rejected — would
  make Backlog and To Do visually indistinguishable at a glance, the opposite
  of what a 4-column board needs).
