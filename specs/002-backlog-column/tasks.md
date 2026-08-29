---

description: "Task list template for feature implementation"
---

# Tasks: Backlog Status Column

**Input**: Design documents from `/specs/002-backlog-column/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/status-values.md, quickstart.md

**Tests**: Included, per Constitution Principle VI (duplicate/conflict coverage is release-blocking) and to lock in the finding from plan.md that this feature needs almost no new production code — the tests are what prove that.

**Organization**: Tasks are grouped by user story (from spec.md, priority order). This feature modifies the existing, already-implemented project from `specs/001-task-management/` — there is no Setup phase, because there is nothing to initialize.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

Existing web app structure from 001: `backend/src/`, `backend/tests/`,
`frontend/src/`, `frontend/tests/`.

---

## Phase 1: Setup

**Not applicable.** This feature extends the already-implemented, already-running project from `specs/001-task-management/` — there is no new project, dependency, or tooling to set up.

---

## Phase 2: Foundational (Blocking Prerequisite)

**Purpose**: Widen the backend's accepted status values — nothing in either user story can be exercised until the backend will accept and persist `"backlog"`.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T001 Add `"backlog"` to the `Status` Pydantic `Literal` in `backend/src/schemas/task.py` and to the `STATUSES` tuple in `backend/src/models/task.py` — no other change (no migration needed; `status` is already a plain `String(20)` column)

**Checkpoint**: The backend will now accept, store, and return `status: "backlog"` on create/update; no UI reflects it yet.

---

## Phase 3: User Story 1 - See Backlog as the First Column (Priority: P1) 🎯 MVP

**Goal**: A "Backlog" column renders as the leftmost column on the board (before "To Do"), correctly displaying any task whose status is `backlog`.

**Independent Test**: Load the board and confirm four columns render in the order Backlog, To Do, In Progress, Done; confirm a task with `status: "backlog"` (created via the API) appears in that column, grouped by schedule the same way as any other column.

### Tests for User Story 1

- [X] T002 [P] [US1] Frontend test: rendering `TaskBoard` with a task of `status: "backlog"` produces four `section[data-status]` elements in the order `backlog, todo, in_progress, done`, with that task appearing in the Backlog section, in `frontend/tests/unit/TaskBoard.test.jsx` (new file)
- [X] T003 [P] [US1] Backend integration test: a task created with `{"status": "backlog"}` round-trips correctly through `GET /api/tasks` (status preserved, appears in the list) in `backend/tests/integration/test_backlog_status.py` (new file) — depends on T001

### Implementation for User Story 1

- [X] T004 [US1] Add `{ value: 'backlog', label: 'Backlog' }` as the **first** entry in the `STATUSES` array in `frontend/src/components/TaskForm.jsx` (this array already drives both `TaskBoard`'s column order and the status `<select>` options, so this one change produces the column order, the column itself, and the ability to pick "Backlog" in the create/edit form) — depends on T002
- [X] T005 [P] [US1] Add a distinct accent color for the Backlog column — a `.task-board section[data-status='backlog'] > h2 { border-bottom-color: ... }` rule (a new color, not reusing the To Do color) in `frontend/src/index.css`

**Checkpoint**: The Backlog column is visible, correctly positioned and styled, and displays any task assigned to it — this alone is independently demoable.

---

## Phase 4: User Story 2 - Assign a Task To or From Backlog (Priority: P2)

**Goal**: Users can create a task directly into Backlog, move a task into/out of Backlog by editing its status, or by dragging it — with every existing rule (duplicate detection, scheduling-conflict detection, drag validation/rollback) applying exactly as it does for any other status.

**Independent Test**: Create a task with status Backlog via the form; edit an existing task's status to/from Backlog; drag a task into and out of the Backlog column, including a drag that should be rejected for a scheduling conflict.

**Note**: Because `TaskColumn`'s drop-zone ids (`column-schedule:${status}` / `column-unscheduled:${status}`), `useDragAndDrop`'s patch resolution, and the backend's duplicate/conflict checks are already fully generic over the status string (no code anywhere branches on the specific value `"todo"`/`"in_progress"`/`"done"`), User Story 1's T004 is expected to already make drag-and-drop and form-based assignment to/from Backlog work with **no additional production code**. This story's tasks are tests that confirm that finding — if any of them fail, that reveals a hidden hardcoded assumption to fix, not a feature still to build.

### Tests for User Story 2

- [X] T006 [P] [US2] Backend contract test: `POST /api/tasks` with `{"status": "backlog"}` succeeds (`201`), and `POST /api/tasks` with no `status` field still defaults to `"todo"` (FR-005, unchanged) — add to `backend/tests/contract/test_tasks_create.py` — depends on T001
- [X] T007 [P] [US2] Backend contract test: `PATCH /api/tasks/{id}` changing `status` to `"backlog"` and back to `"todo"` both succeed — add to `backend/tests/contract/test_tasks_update.py` — depends on T001
- [X] T008 [P] [US2] Backend integration test: duplicate detection (same title + `scheduled_at`, one or both `status: "backlog"`) and scheduling-conflict detection (different title, same `scheduled_at`, one `status: "backlog"`) both still reject exactly as for any other status — add to `backend/tests/integration/test_backlog_status.py` (same file as T003) — depends on T001
- [X] T009 [P] [US2] Frontend test: `useDragAndDrop`'s drop-target resolution produces `{status: "backlog", ...}` for a drop on `column-schedule:backlog` / `column-unscheduled:backlog`, exactly like it does for the existing statuses — add to `frontend/tests/integration/test_drag_rollback.test.jsx` or a new adjacent test file

**Checkpoint**: All create/update/drag paths into and out of Backlog are proven to work through the existing generic implementation, with duplicate/conflict rules intact.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T010 Run the full existing regression suite (`backend`: `./.venv/bin/python -m pytest`; `frontend`: `npm test`) plus the [quickstart.md](./quickstart.md) manual walkthrough, and confirm spec.md Success Criteria SC-001 through SC-004 — 42 backend + 14 frontend tests all pass (up from 37 + 10), production build succeeds, and a live API smoke test confirms a backlog-status task persists and lists correctly alongside todo/in_progress tasks

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — BLOCKS both user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (T001)
- **User Story 2 (Phase 4)**: Depends on Foundational (T001) and on User Story 1's T004 (the `STATUSES` array change) — its tasks are verification of behavior T004 already provides, so in practice do T004 before starting Phase 4's tests
- **Polish (Phase 5)**: Depends on both user stories being complete

### Parallel Opportunities

- T002 and T003 (US1 tests) can run in parallel
- T005 can run in parallel with T002/T003/T004 (different file, no dependency)
- T006, T007, T008, T009 (all US2 tests) can all run in parallel with each other once T001 and T004 are done

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Backend contract test for POST /api/tasks with status=backlog in backend/tests/contract/test_tasks_create.py"
Task: "Backend contract test for PATCH status to/from backlog in backend/tests/contract/test_tasks_update.py"
Task: "Backend integration test for duplicate/conflict rules still applying to backlog in backend/tests/integration/test_backlog_status.py"
Task: "Frontend test for useDragAndDrop resolving backlog drop targets"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 2: Foundational (T001)
2. Complete Phase 3: User Story 1 (T002-T005) — the column exists, is positioned and styled correctly, and displays Backlog tasks
3. **STOP and VALIDATE**: Load the board, confirm column order and styling
4. This alone is demoable even before User Story 2's tests are written, since creating a task directly as Backlog via the API (not yet via the UI form until T004 lands) already displays correctly

### Incremental Delivery

1. Foundational → backend accepts `"backlog"`
2. User Story 1 → column visible, correctly ordered and styled, form can select it (MVP)
3. User Story 2 → confirm (via tests) that create/edit/drag into and out of Backlog all work correctly, including duplicate/conflict rejection
4. Polish → full regression + quickstart pass

---

## Notes

- [P] tasks = different files, no unmet dependencies
- This feature intentionally has almost no "implementation" tasks distinct from
  tests — per plan.md's Constitution Check, the existing code is already
  generic over status values, so the honest task breakdown reflects that
  rather than inventing busywork
- Commit after each task or logical group
- If any User Story 2 test unexpectedly fails, that means a hidden
  status-specific assumption exists somewhere in the codebase — fix it there,
  don't special-case Backlog around it
