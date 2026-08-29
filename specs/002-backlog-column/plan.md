# Implementation Plan: Backlog Status Column

**Branch**: `002-backlog-column` | **Date**: 2026-08-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-backlog-column/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add "Backlog" as a fourth task status, rendered as the leftmost column (before "To
Do"). This is a pure extension of the already-implemented Task Management
Application (`specs/001-task-management/`) — no new architecture, service,
endpoint, or business rule is introduced. It widens two existing enums (the
backend's `Status` type and the frontend's status list) by one value and
reorders/re-colors the board's leftmost slot; every existing rule (duplicate
detection, scheduling-conflict detection, drag-and-drop validation, error
handling) already applies to "any status" generically in the current
implementation, so it applies to Backlog automatically once the value is
accepted as valid.

## Technical Context

**Language/Version**: Same as 001 — Python 3.12 (backend), JavaScript (ES2022+) / React 18 (frontend). No new language or runtime.

**Primary Dependencies**: None added. Reuses the already-implemented FastAPI + SQLAlchemy backend (`backend/`) and React + Vite + `@dnd-kit/core` frontend (`frontend/`) from 001.

**Storage**: Same SQLite database. `Task.status` is already a plain `String(20)` column (not a DB-level `CHECK`/enum constraint) — no migration is needed; only the application-level validation (Pydantic `Literal`) and UI options change.

**Testing**: Same tooling already in place — `pytest` + FastAPI `TestClient` (backend), `Vitest` + React Testing Library (frontend).

**Target Platform**: Unchanged — the same running web application from 001.

**Project Type**: web (existing `backend/` + `frontend/` structure — no new project or service).

**Performance Goals**: Unchanged from 001 (see `../001-task-management/plan.md`).

**Constraints**: Unchanged from 001. Backward compatibility note: existing stored tasks with `status` in `{todo, in_progress, done}` remain fully valid; "backlog" is purely additive to the allowed value set (FR-001).

**Scale/Scope**: One new enum value, one new UI column, zero new endpoints, zero new entities.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Design response |
|---|---|---|
| I. Task Integrity | Duplicate rule stays backend-authoritative and consistently applied | Unchanged — `task_service._ensure_schedule_is_free` already runs identically regardless of status; no branch for "backlog" is added or needed |
| II. Scheduling Integrity | Conflict rule stays backend-authoritative | Unchanged — same function as above; a Backlog task's `scheduled_at` is checked exactly like any other status's |
| III. Drag-and-Drop Integrity | No invalid state via drag; every change persisted via backend | Unchanged mechanism — Backlog becomes just another valid `column-schedule:backlog` / `column-unscheduled:backlog` drop-target id, handled by the existing generic `useDragAndDrop` logic with no special-casing |
| IV. Separation of Concerns | Business rules stay backend-only | The frontend's `STATUSES` list only controls display order and form options — the backend's `Status` Literal is the actual authority on what's a valid status; both are updated together but the backend still rejects any value not in its own Literal |
| V. API-First Development | Contract change documented before frontend relies on it | `contracts/status-values.md` (this feature) documents the additive `Status` enum change to the existing `contracts/tasks-api.md` from 001 |
| VI. Testing and Quality | New behavior gets test coverage | New tests: backend create/update-to-Backlog, duplicate/conflict-still-applies-to-Backlog, frontend column-order rendering |
| VII. Simplicity | No unjustified abstractions | Confirmed — this is a one-line enum addition on each side plus a CSS accent color; no new files beyond tests |
| VIII. Data Integrity & Consistency | Atomic enforcement unaffected | Unchanged — the unique constraint is on `scheduled_at`, not `status`, so it's untouched by adding a status value |

**Result**: PASS — no violations. Complexity Tracking table below is not needed.

**Post-Phase 1 re-check**: `data-model.md` and `contracts/status-values.md` confirm the change is additive-only (one enum value, no schema/migration). Gate remains **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/002-backlog-column/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
├── contracts/            # Phase 1 output (/speckit-plan command)
└── tasks.md               # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

No new directories. Changes land in files that already exist from
`specs/001-task-management/`:

```text
backend/
├── src/
│   ├── models/task.py       # STATUSES tuple gains "backlog"
│   └── schemas/task.py      # Status Literal gains "backlog"
└── tests/
    ├── contract/            # extend test_tasks_create.py / test_tasks_update.py
    └── integration/         # new: test_backlog_status.py

frontend/
├── src/
│   ├── components/TaskForm.jsx   # STATUSES array gains a leading {value:'backlog', label:'Backlog'} entry
│   └── index.css                  # add a distinct accent color for [data-status='backlog']
└── tests/
    └── unit/                       # extend/add a TaskBoard column-order test
```

**Structure Decision**: No structural change — this feature modifies existing
files within the Option 2 (web application) layout already established by
001-task-management. No new services, routers, models, or components.

## Complexity Tracking

*No entries — the Constitution Check above passed without violations, and no
new abstraction, dependency, or project is introduced.*
