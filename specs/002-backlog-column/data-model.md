# Phase 1 Data Model: Backlog Status Column

Full entity definition: see `../001-task-management/data-model.md`. This
feature changes exactly one thing in that model.

## Change: `Task.status` allowed values

| Before (001) | After (this feature) |
|---|---|
| `todo` \| `in_progress` \| `done` | `backlog` \| `todo` \| `in_progress` \| `done` |

- No column type, length, or default changes — `status` remains
  `String(20)`, `nullable=False`, `default="todo"` (FR-005: the default is
  unchanged; a task is only ever `backlog` if explicitly set).
- No migration required: SQLite has no `CHECK` constraint on this column
  today, so existing rows and the schema itself are untouched. The new value
  is accepted purely because the Pydantic `Literal` in `TaskCreate`/`TaskUpdate`
  is widened to include it.
- All other fields, constraints (the `scheduled_at` uniqueness backstop), and
  validation rules from 001's data model are unchanged and apply to `backlog`
  tasks identically (FR-006).

## Display ordering (not a stored field)

Column order on the board is `backlog, todo, in_progress, done` (FR-002). As
in 001, this is a UI-only concern — no `position`/`order` field is persisted;
the frontend's status list literally defines the left-to-right order.
