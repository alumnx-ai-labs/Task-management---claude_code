# API Contract: Tasks

Base path: `/api/tasks`. All bodies are JSON (`Content-Type: application/json`). All
timestamps are ISO-8601 UTC strings (e.g., `"2026-09-03T14:30:00Z"`).

This contract is authored before any frontend integration work, per Constitution
Principle V. Backend contract tests (`backend/tests/contract/`) assert every endpoint
matches this document; frontend code MUST NOT call an endpoint or field not defined here
without updating this file first.

## Shared error envelope

Every non-2xx response has this shape:

```json
{
  "error": {
    "code": "DUPLICATE_TASK",
    "message": "A task titled \"Team sync\" is already scheduled for 2026-09-03 14:30.",
    "details": { "conflicting_task_id": "b3f1..." }
  }
}
```

| `code` | HTTP status | When |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Missing/blank title, malformed `scheduled_at`, invalid `status` value |
| `DUPLICATE_TASK` | 409 | Same title + same `scheduled_at` as an existing task (FR-010) |
| `SCHEDULING_CONFLICT` | 409 | Same `scheduled_at` as an existing task, different title (FR-011) |
| `TASK_NOT_FOUND` | 404 | `id` does not exist (Edge Cases — update/delete after deletion) |

`details.conflicting_task_id` is included for `DUPLICATE_TASK` and
`SCHEDULING_CONFLICT` so the frontend can, optionally, link to or highlight the
conflicting task (FR-011: "identifying the conflicting date/time and, where possible,
the conflicting task").

## `GET /api/tasks`

Returns all tasks (FR-003). No pagination — scale/scope is "low hundreds of tasks"
(plan.md Technical Context); pagination would be premature per Principle VII.

**200 OK**

```json
{
  "tasks": [
    {
      "id": "b3f1c2...",
      "title": "Team sync",
      "description": "Weekly status check-in",
      "scheduled_at": "2026-09-03T14:30:00Z",
      "status": "todo",
      "created_at": "2026-08-29T10:00:00Z",
      "updated_at": "2026-08-29T10:00:00Z"
    }
  ]
}
```

## `POST /api/tasks`

Creates a task (FR-001). Runs full validation → duplicate check → conflict check
(research.md §3) before insert.

**Request**

```json
{
  "title": "Team sync",
  "description": "Weekly status check-in",
  "scheduled_at": "2026-09-03T14:30:00Z",
  "status": "todo"
}
```

`description`, `scheduled_at`, `status` are optional (`status` defaults to `"todo"`).

**201 Created** — full `Task` object (same shape as the `GET` list item).

**Errors**: `VALIDATION_ERROR` (422), `DUPLICATE_TASK` (409), `SCHEDULING_CONFLICT`
(409).

## `PATCH /api/tasks/{id}`

Updates a task. Used for every kind of change — field edits, status changes,
rescheduling, **and drag-and-drop moves** (FR-004, FR-006, FR-008): there is no
separate "move" endpoint (Principle VII). Only the fields present in the body are
changed; omitted fields are left as-is.

**Request** (example: a drag-and-drop move that changes both column and time slot)

```json
{
  "status": "in_progress",
  "scheduled_at": "2026-09-04T09:00:00Z"
}
```

**200 OK** — full, updated `Task` object.

**Errors**: `VALIDATION_ERROR` (422), `DUPLICATE_TASK` (409), `SCHEDULING_CONFLICT`
(409), `TASK_NOT_FOUND` (404). A `scheduled_at` update that exactly matches the task's
own current value is never a conflict (FR-013) — the conflict/duplicate checks exclude
the task's own `id`.

## `DELETE /api/tasks/{id}`

Deletes a task (FR-005).

**204 No Content** on success.

**Errors**: `TASK_NOT_FOUND` (404).

## Endpoints deliberately not included

- **Bulk create/update/delete**: out of scope (spec Assumptions).
- **A dedicated "move" or "reorder" endpoint**: drag-and-drop reuses `PATCH
  /api/tasks/{id}` (see above) — introducing a second endpoint for the same
  state transition would duplicate validation logic and risk the two paths drifting
  apart (Principle IV, VIII).
- **Authentication endpoints**: no user accounts in this feature (spec Assumptions).
