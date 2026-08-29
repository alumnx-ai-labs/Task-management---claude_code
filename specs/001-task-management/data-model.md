# Phase 1 Data Model: Task Management Application

Source: [spec.md](./spec.md) Key Entities + Functional Requirements, resolved against
the decisions in [research.md](./research.md).

## Entity: Task

The application has a single entity. There are no relationships to model (no users,
no tags, no sub-tasks — all out of scope per spec Assumptions).

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID (string) | Yes, backend-generated | Assigned at creation (FR-002); never reused; never client-supplied |
| `title` | string | Yes | Non-empty after trimming whitespace (FR-001, Edge Cases); max length 200 chars (reasonable default — not spec-mandated, prevents unbounded storage) |
| `description` | string | No | Optional; no enforced max length at the API layer, but the UI truncates long descriptions for display (Edge Cases) |
| `scheduled_at` | datetime (UTC, ISO-8601) | No | `NULL` = unscheduled (FR-001, Edge Cases). Precision used for comparison: minute (research.md §4). No duration/end time field — tasks are instantaneous points in time (Clarifications) |
| `status` | enum: `todo`, `in_progress`, `done` | Yes | Defaults to `todo` on creation if not supplied (User Story 1, Acceptance Scenario 1). Fixed set per spec Assumptions — no custom statuses |
| `created_at` | datetime (UTC) | Yes, backend-generated | Set once at creation |
| `updated_at` | datetime (UTC) | Yes, backend-generated | Updated on every successful create/update, including drag-and-drop moves |

### Validation rules

- **Title**: required, non-blank after trim (FR-001, Edge Cases: whitespace-only titles
  are rejected as if empty).
- **Status**: must be one of the three fixed values; unrecognized values are rejected as
  a validation error (FR-015), not silently coerced to a default.
- **scheduled_at**: if present, must be a valid ISO-8601 datetime; invalid formats are
  rejected as a validation error (FR-015) before any duplicate/conflict check runs.

### Uniqueness / integrity constraints (Constitution Principles I, II, VIII)

- **Duplicate rule** (FR-010): two tasks are duplicates when their normalized titles
  match — lowercased, leading/trailing whitespace trimmed, and internal whitespace runs
  collapsed to a single space — AND `scheduled_at` matches exactly. A task with `scheduled_at IS NULL` is
  never a duplicate of anything (FR-010). Enforced in the service layer, checked before
  the conflict rule (research.md §3), on both create and update (FR-009, FR-010 — no
  exemption for any status per FR-018). On update, the check excludes the task's own
  `id` — a task is never compared against its own existing record (FR-010), mirroring
  the self-update exception already defined for the conflict rule below.
- **Scheduling-conflict rule** (FR-011, FR-012): two tasks conflict when `scheduled_at`
  matches exactly (to the minute — any seconds/sub-second precision on the input is
  truncated, not rounded, before comparison), regardless of title. `NULL` never
  conflicts with anything. Enforced in the service layer on create/update/drag-and-drop
  (FR-008), with
  a self-update exception (FR-013): a task being saved with its own unchanged
  `scheduled_at` does not conflict with itself (the check excludes the task's own `id`).
- **Atomicity backstop** (Principle VIII): a database-level unique index on
  `scheduled_at` (excluding `NULL`, which SQL unique indexes already treat as distinct
  per row) ensures that even if two requests pass the service-layer check concurrently,
  only one `INSERT`/`UPDATE` succeeds; the other raises an `IntegrityError` that the API
  layer maps to the same `409` conflict response used for the ordinary case (Edge Cases:
  race condition — "exactly one MUST succeed").
- **Status has no restricted transitions**: any status may move to any other status via
  update or drag-and-drop (spec does not define a workflow state machine beyond the
  fixed set of values), including tasks in `done` (FR-018 — no status-based exemption
  from any rule).

## Derived / view-only concepts (not stored fields)

- **"Unscheduled" grouping** (FR-017): a UI-only grouping of tasks with `scheduled_at IS
  NULL` within their status column — not a database field.
- **Column position** (FR-006): the task's `status` field is the column; ordering within
  a column is derived by sorting on `scheduled_at` (unscheduled tasks grouped
  separately) — no separate `position`/`order` field is persisted, avoiding an
  unnecessary abstraction (Principle VII).
