# Quickstart: Validating the Task Management Application

This is a validation guide, not an implementation reference — it proves the feature
works end-to-end once built. Field/endpoint details live in
[data-model.md](./data-model.md) and [contracts/tasks-api.md](./contracts/tasks-api.md);
this file only sequences runnable checks against those contracts.

## Prerequisites

- Python 3.12+ with the backend's dependencies installed (`backend/`)
- Node.js (LTS) with the frontend's dependencies installed (`frontend/`)
- No external services required — SQLite is a local file (research.md §2)

## Run the stack

```bash
# Terminal 1 — backend
cd backend
uvicorn src.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

Open the frontend's dev URL in a browser. The board should load empty on first run.

## Backend contract & integration tests

```bash
cd backend
pytest tests/contract tests/integration tests/unit
```

These are the release-blocking tests required by Constitution Principle VI. At minimum
they must include:

1. **Duplicate rejected** — `POST /api/tasks` twice with the same title + `scheduled_at`
   → second call returns `409 DUPLICATE_TASK` (FR-009, FR-010).
2. **Conflict rejected (different title, same time)** — `POST` two tasks with different
   titles but the same `scheduled_at` → second call returns `409 SCHEDULING_CONFLICT`
   (FR-011).
3. **Self-update is not a conflict** — `PATCH` a task with its own current
   `scheduled_at` → `200 OK`, not `409` (FR-013).
4. **Update creates a duplicate** — create two tasks with different schedules, then
   `PATCH` one to match the other's title + `scheduled_at` → `409 DUPLICATE_TASK`
   (FR-009/FR-010 applying to updates, not just creates).
5. **Drag-and-drop move persists through the same validation path** — `PATCH` a task's
   `status`/`scheduled_at` as a drag-and-drop move would, onto a slot occupied by
   another task → `409 SCHEDULING_CONFLICT`, and onto a free slot → `200 OK` with the
   new column/position reflected on a subsequent `GET /api/tasks` (FR-006, FR-008).
6. **Concurrent create race** — fire two `POST` requests for the same
   title+`scheduled_at` (or same `scheduled_at`, different titles) concurrently →
   exactly one `201`, the other `409` (Edge Cases; Principle VIII, backed by the unique
   DB constraint).

## Manual end-to-end walkthrough (maps to spec User Stories)

1. **Create and view** (User Story 1): create a task with only a title → appears in the
   `To Do` column with "no scheduled date/time". Create a second task with a
   description, date/time, and status → appears in the correct column with all fields
   visible.
2. **Duplicate/conflict prevention** (User Story 2): attempt to create a task that
   duplicates the first one → see a clear "duplicate" error. Attempt to create a
   different-titled task at the same date/time as an existing one → see a clear
   "conflict" error naming the date/time.
3. **Update** (User Story 3): edit a task's title/description, change its status via the
   edit form, reschedule it to a free slot → each change is reflected immediately.
   Attempt to reschedule it onto an occupied slot → rejected, original schedule
   retained.
4. **Drag-and-drop** (User Story 4): drag a task to a different status column → status
   updates. Drag a task to a different, free date/time position → schedule updates.
   Drag a task onto an occupied date/time → rejected, card visually returns to its
   original position, error shown.
5. **Delete** (User Story 5): delete a task → disappears immediately; refresh the page
   → it does not return.
6. **Persistence** (FR-014): after steps 1–5, refresh the browser → the board reloads
   with the exact same tasks, columns, and schedules as before the refresh.
7. **Done tasks stay editable** (Clarifications, FR-018): move a task to `Done`, then
   reschedule/drag it again, and separately attempt to create a duplicate of it → the
   same rules apply as for any other status (no special-casing).

## Success criteria check

Each item in spec.md's [Success Criteria](./spec.md#success-criteria-mandatory)
(SC-001–SC-007) should be observably true after completing the walkthrough above —
in particular SC-002/SC-003 (100% of duplicate/conflict attempts rejected) are exercised
by the automated tests in the previous section, not just the manual walkthrough.

**SC-007 (error message clarity) requires a small usability check, not just a
functional one**: trigger each of the four rejection types (validation, duplicate,
conflict, not-found) in the running app, then show each resulting message — with no
other context — to someone who has not read this spec (a teammate, or yourself after a
break). Ask them to state in their own words what went wrong. If they can do so for at
least 9 of 10 messages shown across a few people, SC-007 is satisfied; if not, revise
the corresponding error message text (not the underlying error code) and re-check.
