---

description: "Task list template for feature implementation"
---

# Tasks: Task Management Application

**Input**: Design documents from `/specs/001-task-management/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/tasks-api.md, quickstart.md

**Tests**: Included. Constitution Principle VI marks automated coverage of duplicate
prevention, scheduling-conflict detection, and drag-and-drop persistence as
release-blocking; contract/integration tests for the remaining CRUD endpoints are
included for the same API-First/Testing-and-Quality reasons and to match the test
directory structure already established in plan.md.

**Organization**: Tasks are grouped by user story (from spec.md, priority order) to
enable independent implementation and testing of each story. User Story 2 owns the
*entire* backend `PATCH` (update) endpoint — not just the duplicate/conflict checks —
because an update cannot be validated without also being able to persist it; User
Story 3 then adds only the frontend editing experience on top of that already-complete,
already-tested endpoint. (An earlier draft split the update endpoint's implementation
across User Story 2 and User Story 3, which made User Story 2's own self-update test
unrunnable until User Story 3 was also done — see the `/speckit-analyze` finding this
revision resolves.)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Web app structure per [plan.md](./plan.md#project-structure): `backend/src/`,
`backend/tests/`, `frontend/src/`, `frontend/tests/`. All API paths are prefixed
`/api/tasks`, matching [contracts/tasks-api.md](./contracts/tasks-api.md).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create the directory skeleton per plan.md: `backend/src/{models,schemas,services,api}`, `backend/tests/{contract,integration,unit}`, `frontend/src/{components,pages,hooks,services}`, `frontend/tests/{unit,integration}`
- [X] T002 Initialize the backend Python project in `backend/` (`pyproject.toml` or `requirements.txt`) with dependencies: fastapi, sqlalchemy, pydantic, uvicorn
- [X] T003 [P] Initialize the frontend project in `frontend/` via Vite's React (JavaScript) template, and add the `@dnd-kit/core` dependency to `frontend/package.json`
- [X] T004 [P] Add backend test/dev dependencies (pytest, httpx) to `backend/pyproject.toml`
- [X] T005 [P] Add frontend test dependencies (Vitest, React Testing Library) and a `frontend/vite.config.js` test block

**Checkpoint**: Both project skeletons exist and install cleanly.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Define the `Task` SQLAlchemy model (id, title, description, scheduled_at, status, created_at, updated_at) with a unique constraint on `scheduled_at` in `backend/src/models/task.py`, per [data-model.md](./data-model.md)
- [X] T007 Set up the SQLite engine, session factory, and table-creation call in `backend/src/db.py`
- [X] T008 [P] Define Pydantic schemas `TaskCreate`, `TaskUpdate`, `TaskRead` in `backend/src/schemas/task.py` matching the request/response shapes in [contracts/tasks-api.md](./contracts/tasks-api.md)
- [X] T009 Create the FastAPI app entrypoint with CORS enabled for the Vite dev origin in `backend/src/main.py` (depends on T007)
- [X] T010 Implement the shared error envelope and exception handlers (`VALIDATION_ERROR`→422, `DUPLICATE_TASK`/`SCHEDULING_CONFLICT`→409, `TASK_NOT_FOUND`→404) registered on the app in `backend/src/api/errors.py` (depends on T009)
- [X] T011 [P] Create the frontend REST client wrapper (`fetch`, throws a typed `ApiError` parsed from the error envelope) in `frontend/src/services/api.js`, per [contracts/tasks-api.md](./contracts/tasks-api.md)
- [X] T012 [P] Create the frontend app entrypoint and an empty `BoardPage` scaffold in `frontend/src/main.jsx` and `frontend/src/pages/BoardPage.jsx`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Create and View Tasks on the Board (Priority: P1) 🎯 MVP

**Goal**: Users can create a task (title required; description, schedule, status
optional) and see all tasks organized in the combined status/time board.

**Independent Test**: Create tasks with varying fields via the running app/API and
confirm each appears in the correct status column, ordered by scheduled date/time
(unscheduled tasks in their own grouping), with title/schedule/status all visible.

### Tests for User Story 1

- [X] T013 [P] [US1] Contract test for `POST /api/tasks` in `backend/tests/contract/test_tasks_create.py`, covering: title-only success; full-fields success; missing-title → 422; whitespace-only-title → 422 (treated the same as missing, per spec.md Edge Cases); two separately created tasks receive distinct, backend-generated `id` values (FR-002)
- [X] T014 [P] [US1] Contract test for `GET /api/tasks` (empty list, populated list shape) in `backend/tests/contract/test_tasks_list.py`
- [X] T015 [P] [US1] Integration test: a created task is retrievable via a fresh DB session, proving persistence survives a simulated restart (FR-014) in `backend/tests/integration/test_persistence.py`

### Implementation for User Story 1

- [X] T016 [US1] Implement `create_task` and `list_tasks` in `backend/src/services/task_service.py` (trims/validates title, defaults `status="todo"`) — depends on T006, T007, T008
- [X] T017 [US1] Implement `POST /api/tasks` and `GET /api/tasks` routes in `backend/src/api/tasks.py` — depends on T016, T010
- [X] T018 [P] [US1] Implement `TaskForm` component (title/description/date-time/status inputs, disables submit while title is blank) in `frontend/src/components/TaskForm.jsx`
- [X] T019 [P] [US1] Implement `TaskCard` component (renders title, scheduled date/time or "unscheduled", status, truncated description) in `frontend/src/components/TaskCard.jsx`
- [X] T020 [US1] Implement `TaskColumn` (one per status, sorts contained tasks by `scheduled_at` with an "unscheduled" group) and `TaskBoard` (renders the three `TaskColumn`s) in `frontend/src/components/TaskColumn.jsx` and `frontend/src/components/TaskBoard.jsx` — depends on T019
- [X] T021 [US1] Implement `useTasks` hook (loads tasks on mount via `GET`, exposes `createTask`) wired to `services/api.js` in `frontend/src/hooks/useTasks.js` — depends on T011, T017
- [X] T022 [US1] Wire `BoardPage` to `useTasks`, `TaskBoard`, and `TaskForm` for the create-and-view flow in `frontend/src/pages/BoardPage.jsx` — depends on T018, T020, T021

**Checkpoint**: User Story 1 is fully functional and testable independently — tasks can be created and viewed, organized on the board, and persist across a backend restart.

---

## Phase 4: User Story 2 - Backend-Enforced Duplicate and Scheduling-Conflict Prevention (Priority: P1)

**Goal**: The backend independently rejects duplicate tasks (same title + same
scheduled date/time) and scheduling conflicts (same scheduled date/time, any title),
on both create and update, with a clear, specific error — regardless of what the
frontend does. This story owns the complete `PATCH /api/tasks/{id}` endpoint (not just
its validation checks), since the checks cannot be proven correct without a real,
persisting update to check them against.

**Independent Test**: Call the create endpoint twice with duplicate-defining details
and confirm the second is rejected with a `DUPLICATE_TASK` error; create two
different-titled tasks at the same date/time and confirm the second is rejected with a
`SCHEDULING_CONFLICT` error; confirm re-saving a task with its own unchanged schedule
succeeds; confirm updating one task's title/schedule to match another's is also
rejected; confirm a `Done`-status task is not exempt from any of this (FR-018).

### Tests for User Story 2

- [X] T023 [P] [US2] Integration test: creating a task with the same title (case-insensitive, trimmed) + same `scheduled_at` as an existing task is rejected with `409 DUPLICATE_TASK` in `backend/tests/integration/test_duplicate_prevention.py`
- [X] T024 [P] [US2] Integration test: creating a task with a different title but the same `scheduled_at` as an existing task is rejected with `409 SCHEDULING_CONFLICT` in `backend/tests/integration/test_scheduling_conflict.py`
- [X] T025 [P] [US2] Integration test: updating a task with its own current `scheduled_at` (no change) succeeds rather than being flagged as a self-conflict (FR-013) in `backend/tests/integration/test_self_update_no_conflict.py`
- [X] T026 [P] [US2] Integration test: two concurrent create requests for the same duplicate/conflicting `scheduled_at` — exactly one succeeds (`201`), the other is rejected (`409`), proving the DB unique constraint backstops the service-layer check (Principle VIII) in `backend/tests/integration/test_concurrent_create_race.py`
- [X] T027 [P] [US2] Contract test for `PATCH /api/tasks/{id}` in `backend/tests/contract/test_tasks_update.py`, covering: a plain field-update success; unknown id → `404 TASK_NOT_FOUND`
- [X] T028 [P] [US2] Integration test: updating a task's title/schedule to match another existing task's title + `scheduled_at` is rejected with `409 DUPLICATE_TASK` (the duplicate rule applies to updates, not just creates — FR-009/FR-010), and a task updated with its own unchanged title+schedule is never flagged as a duplicate of itself (FR-010's self-exclusion) in `backend/tests/integration/test_update_duplicate_rejected.py`
- [X] T029 [P] [US2] Integration test: a task in `done` status can still be updated, rescheduled, and is still rejected for duplicate/conflict violations exactly like a task in any other status (FR-018) in `backend/tests/integration/test_done_task_not_exempt.py`

### Implementation for User Story 2

- [X] T030 [US2] Implement the duplicate check (normalized-title + `scheduled_at` match, excluding the task's own id per FR-010) in `backend/src/services/task_service.py` — depends on T016
- [X] T031 [US2] Implement the scheduling-conflict check (`scheduled_at` match regardless of title, excluding the task's own id, truncating sub-minute precision before comparison per FR-012), run after the duplicate check per [research.md §3](./research.md) — depends on T030
- [X] T032 [US2] Catch the DB `IntegrityError` raised by the unique constraint on concurrent writes and translate it to the same `409 SCHEDULING_CONFLICT`/`DUPLICATE_TASK` response as the service-layer check — depends on T006, T031
- [X] T033 [US2] Implement `update_task` in `backend/src/services/task_service.py` — a full partial update of title/description/status/scheduled_at that reuses the duplicate check (T030) and conflict check (T031), applying identically regardless of the task's current or new status (FR-018) — depends on T030, T031, T032, T016
- [X] T034 [US2] Implement `POST /api/tasks` (create) and `PATCH /api/tasks/{id}` (update, including `404 TASK_NOT_FOUND` for an unknown id) routes, both wired to the duplicate/conflict checks, in `backend/src/api/tasks.py` — depends on T033, T017, T010
- [X] T035 [P] [US2] Implement `ErrorBanner` component that renders a backend `ApiError`'s message in `frontend/src/components/ErrorBanner.jsx`
- [X] T036 [US2] Surface `DUPLICATE_TASK`/`SCHEDULING_CONFLICT` errors from task creation via `ErrorBanner` in `frontend/src/components/TaskForm.jsx` and `frontend/src/pages/BoardPage.jsx` — depends on T035, T021, T034

**Checkpoint**: User Stories 1 and 2 both work independently — the board's core
integrity guarantee (no duplicates, no double-booked times) is enforced end-to-end for
both creates and updates, with no status-based exemption.

---

## Phase 5: User Story 3 - Update Task Details, Status, and Schedule (Priority: P2)

**Goal**: Users can edit a task's title/description, change its status, and
reschedule it through the UI. The backend `PATCH` endpoint this relies on — including
its duplicate/conflict validation — is already fully built and tested by User Story 2;
this story adds only the frontend editing experience on top of it.

**Independent Test**: Edit an existing task's fields through the UI and confirm the
board reflects them; change status and confirm the column updates; reschedule to a
free slot (succeeds) and to an occupied slot (rejected via the already-proven backend
rule, original schedule retained in the UI).

### Implementation for User Story 3

- [X] T037 [P] [US3] Add an edit mode to `TaskCard`/`TaskForm` (pre-fills existing values, submits via `PATCH` instead of `POST`) in `frontend/src/components/TaskCard.jsx` and `frontend/src/components/TaskForm.jsx` — depends on T018, T019
- [X] T038 [US3] Wire the edit-and-reschedule flow (submit → `PATCH /api/tasks/{id}` → update local state or show the conflict/duplicate/not-found error via `ErrorBanner`) in `frontend/src/hooks/useTasks.js` and `frontend/src/pages/BoardPage.jsx` — depends on T034, T037, T035

**Checkpoint**: User Stories 1-3 all work independently — tasks are fully editable
through the UI with backend-enforced integrity preserved.

---

## Phase 6: User Story 4 - Reorganize Tasks via Drag-and-Drop (Priority: P2)

**Goal**: Users can drag a task to a different status column (changes status) or to a
different date/time position (changes schedule), with invalid drops rejected and
rolled back, and every change persisted through the same validated `PATCH` endpoint
User Story 2 already built.

**Independent Test**: Drag a task to a valid new column/time and confirm both the
on-screen position and the underlying record update; drag a task onto an
already-occupied date/time and confirm it is rejected with the card visually
returning to its original position.

### Tests for User Story 4

- [X] T039 [P] [US4] Integration test: a `PATCH` shaped like a drag-and-drop move (`status` and/or `scheduled_at` change) onto a free slot succeeds and is reflected in a subsequent `GET /api/tasks` (FR-006, FR-008) in `backend/tests/integration/test_drag_drop_persistence.py`
- [X] T040 [P] [US4] Integration test: a `PATCH` shaped like a drag-and-drop move onto an occupied `scheduled_at` is rejected with `409 SCHEDULING_CONFLICT`, leaving the original task untouched, in `backend/tests/integration/test_drag_drop_conflict.py`

### Implementation for User Story 4

- [X] T041 [US4] Wrap `TaskBoard`/`TaskColumn` in a `@dnd-kit/core` `DndContext` with droppable column/time-slot targets in `frontend/src/components/TaskBoard.jsx` and `frontend/src/components/TaskColumn.jsx` — depends on T020
- [X] T042 [US4] Implement `useDragAndDrop` hook: on drag end, compute the `{status?, scheduled_at?}` patch from the drop target, apply an optimistic local update, call `PATCH /api/tasks/{id}`, and roll back the optimistic change on any error response in `frontend/src/hooks/useDragAndDrop.js` — depends on T034, T021, T035
- [X] T043 [US4] Wire the drag-end handler to `useDragAndDrop` and `ErrorBanner` in `frontend/src/pages/BoardPage.jsx` — depends on T041, T042

**Checkpoint**: User Stories 1-4 all work independently — drag-and-drop is fully
validated, persisted, and rejects/rolls back invalid moves exactly like a form edit.

---

## Phase 7: User Story 5 - Delete a Task (Priority: P3)

**Goal**: Users can delete a task; deleting or updating an already-deleted task
returns a clear "not found" error instead of failing silently.

**Independent Test**: Delete a task and confirm it disappears immediately and does
not reappear after a refresh; attempt to delete/update it again and confirm a clear
not-found error.

### Tests for User Story 5

- [X] T044 [P] [US5] Contract test for `DELETE /api/tasks/{id}` (success → 204, unknown/already-deleted id → 404 `TASK_NOT_FOUND`) in `backend/tests/contract/test_tasks_delete.py`

### Implementation for User Story 5

- [X] T045 [US5] Implement `delete_task` (raises `TASK_NOT_FOUND` for an unknown id) in `backend/src/services/task_service.py` — depends on T006, T007
- [X] T046 [US5] Implement `DELETE /api/tasks/{id}` route in `backend/src/api/tasks.py` — depends on T045, T010
- [X] T047 [P] [US5] Add a delete action (with a confirmation step) to `TaskCard` in `frontend/src/components/TaskCard.jsx` — depends on T019
- [X] T048 [US5] Wire the delete flow (`DELETE` call → remove from local state, or show the not-found error via `ErrorBanner` if it was already gone) in `frontend/src/hooks/useTasks.js` and `frontend/src/pages/BoardPage.jsx` — depends on T046, T047, T035

**Checkpoint**: All five user stories are independently functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T049 [P] Frontend component tests (`TaskForm` blank-title validation, `TaskCard` rendering of unscheduled/long-description tasks, `ErrorBanner` message display) using Vitest + React Testing Library in `frontend/tests/unit/`
- [X] T050 [P] Frontend integration test: an optimistic drag update rolls back and shows an error when the mocked API rejects the `PATCH` in `frontend/tests/integration/test_drag_rollback.test.jsx`
- [X] T051 Handle a network-unreachable backend by surfacing a clear connectivity error via `ErrorBanner` (no operation is shown as successful) in `frontend/src/services/api.js` and `frontend/src/hooks/useTasks.js`
- [X] T052 [P] Backend unit tests for the duplicate/conflict comparison logic in isolation (title normalization, exact-minute time matching including sub-minute truncation, self-id exclusion for both the duplicate and conflict checks) in `backend/tests/unit/test_task_rules.py`
- [X] T053 Run the full [quickstart.md](./quickstart.md) walkthrough end-to-end, including its SC-007 usability check, and confirm spec.md Success Criteria SC-001 through SC-007 — automated coverage (37 backend + 10 frontend tests) plus a live manual smoke test of every endpoint/business rule via the running backend confirm SC-001–SC-006; **SC-007's usability check still needs a human reviewer** (see Completion Report)
- [X] T054 [P] Add brief run instructions in `backend/README.md` and `frontend/README.md`, referencing quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 (both P1) should be done first, in either order, before US3/US4/US5
  - US3 and US4 both depend directly on User Story 2's complete `PATCH /api/tasks/{id}`
    endpoint (T034) — they do **not** depend on each other, and can proceed in parallel
    once US2 is done
  - US5 has no dependency on US2/US3/US4 and could be done any time after Foundational
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — no dependency on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2); it builds the complete `PATCH /api/tasks/{id}` endpoint (T034), which User Story 3 and User Story 4 both reuse directly
- **User Story 3 (P2)**: Can start after User Story 2's T034 lands; adds only frontend editing UI, no new backend work
- **User Story 4 (P2)**: Can start after User Story 2's T034 lands; independent of User Story 3
- **User Story 5 (P3)**: Can start after Foundational — no dependency on US2/US3/US4

### Within Each User Story

- Tests are written before their corresponding implementation tasks
- Models/schemas before services
- Services before API routes
- Backend route before the frontend flow that calls it
- Story complete before moving to the next priority

### Parallel Opportunities

- T003, T004, T005 (Setup) can run in parallel once T001/T002 exist
- T008, T011, T012 (Foundational) can run in parallel with each other
- All test tasks within a story marked [P] can run in parallel (different files)
- T018 and T019 (US1 components) can run in parallel
- T023-T029 (US2 tests) can all run in parallel
- Once User Story 2's T034 is done, User Story 3 and User Story 4 can be staffed in
  parallel by different developers — they no longer depend on each other

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Integration test for duplicate rejection in backend/tests/integration/test_duplicate_prevention.py"
Task: "Integration test for scheduling-conflict rejection in backend/tests/integration/test_scheduling_conflict.py"
Task: "Integration test for self-update non-conflict in backend/tests/integration/test_self_update_no_conflict.py"
Task: "Integration test for concurrent create race in backend/tests/integration/test_concurrent_create_race.py"
Task: "Contract test for PATCH /api/tasks/{id} in backend/tests/contract/test_tasks_update.py"
Task: "Integration test for update-creates-duplicate rejection in backend/tests/integration/test_update_duplicate_rejected.py"
Task: "Integration test for Done-status tasks not being exempt in backend/tests/integration/test_done_task_not_exempt.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

Both are Priority P1 in spec.md — the board is not trustworthy without backend-enforced
integrity, so the MVP is the pair together, not User Story 1 alone:

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (create/view)
4. Complete Phase 4: User Story 2 (duplicate/conflict enforcement, full `PATCH` endpoint)
5. **STOP and VALIDATE**: Run the User Story 1 + 2 sections of quickstart.md
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Add User Story 2 → Test both together → Deploy/Demo (MVP!)
3. Add User Story 3 (update/reschedule UI) → Test independently → Deploy/Demo
4. Add User Story 4 (drag-and-drop) → Test independently → Deploy/Demo
5. Add User Story 5 (delete) → Test independently → Deploy/Demo
6. Polish phase → Final quickstart.md validation pass

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. One developer completes User Story 2 in full (including T034, the complete `PATCH`
   endpoint), since both User Story 3 and User Story 4 build on it directly
3. Once T034 lands:
   - Developer A: User Story 1 frontend (can start immediately after Foundational,
     doesn't need US2)
   - Developer B: User Story 3
   - Developer C: User Story 4
   - Developer D: User Story 5 (fully independent)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no unmet dependencies
- [Story] label maps task to specific user story for traceability
- Every duplicate/conflict/drag-and-drop test task is release-blocking per
  Constitution Principle VI — do not skip them to "save time"
- User Story 2 intentionally owns the entire `PATCH /api/tasks/{id}` endpoint (not just
  its validation), so its own tests (e.g., T025's self-update check) never depend on a
  later-phase story's work
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break
  independence beyond the explicitly noted US3/US4 → US2 reuse
