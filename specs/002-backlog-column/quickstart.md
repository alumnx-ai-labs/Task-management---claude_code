# Quickstart: Validating the Backlog Status Column

Field/contract details live in [data-model.md](./data-model.md) and
[contracts/status-values.md](./contracts/status-values.md); this file only
sequences runnable checks. Prerequisites and run commands are unchanged from
`../001-task-management/quickstart.md` — start the same backend and frontend.

## Backend tests

```bash
cd backend
./.venv/bin/python -m pytest tests/integration/test_backlog_status.py -v
```

At minimum this should confirm:

1. **Create directly into Backlog** — `POST /api/tasks` with
   `"status": "backlog"` → `201`, response has `status: "backlog"` (FR-003).
2. **Update into/out of Backlog** — `PATCH` an existing task's `status` to
   `"backlog"` and back to `"todo"` → both succeed (FR-003).
3. **Default unaffected** — `POST /api/tasks` with no `status` field still
   returns `status: "todo"` (FR-005).
4. **Duplicate/conflict rules still apply** — creating two Backlog tasks with
   the same title + `scheduled_at` → `409 DUPLICATE_TASK`; a Backlog task and
   a To Do task sharing a `scheduled_at` → `409 SCHEDULING_CONFLICT` (FR-006).

## Manual walkthrough (maps to spec.md User Stories)

1. **Column presence and order** (User Story 1): load the board → confirm four
   columns appear in the order Backlog, To Do, In Progress, Done, and that
   Backlog is empty on a fresh database.
2. **Create into Backlog** (User Story 2): use the task form's status dropdown
   to create a task directly as Backlog → it appears in the Backlog column.
3. **Move via edit** (User Story 2): edit an existing To Do task, change its
   status to Backlog → it moves to the Backlog column; edit it again back to
   To Do → it moves back.
4. **Move via drag** (User Story 2): drag a task from another column into
   Backlog → status updates; drag a Backlog task onto another task's occupied
   time slot in a different column → rejected with a conflict error, card
   returns to Backlog.
5. **Pre-existing data untouched** (Edge Cases / SC-004): confirm tasks
   created before this change (in To Do/In Progress/Done) remain in their
   original column after the change ships — nothing is auto-moved to Backlog.
