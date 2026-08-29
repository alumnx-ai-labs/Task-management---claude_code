# Implementation Plan: Task Management Application

**Branch**: `001-task-management` | **Date**: 2026-08-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-task-management/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

A single combined task board: status columns (To Do / In Progress / Done) with tasks
ordered by scheduled date/time within each column. A React SPA renders the board and
drives all reads/writes through a REST API served by a Python (FastAPI) backend backed
by a SQLite database. The backend is the sole authority for business rules — duplicate
detection (same title + same scheduled date/time) and scheduling-conflict detection (no
two tasks may share the same scheduled date/time) — applied identically to creates,
updates, and drag-and-drop moves (per Constitution Principles I, II, III, IV). A unique
database constraint on the task's scheduled timestamp backstops the application-level
checks so that concurrent requests cannot both succeed (Principle VIII).

**Overall architecture**: Two independently deployable units — `frontend/` (React SPA,
build via Vite, plain JavaScript) and `backend/` (FastAPI service) — communicating only
over a versioned JSON REST API. No shared code, database access, or process boundary
crossing between them (Principle IV). See [research.md](./research.md) for the
technology-choice rationale.

**Frontend architecture**: A single `BoardPage` renders `TaskColumn` components (one per
status) built from a `useTasks` hook that owns the in-memory task list and talks to the
API via a thin `services/api.js` REST client (native `fetch`, no HTTP library needed —
Principle VII). Drag-and-drop is provided by `@dnd-kit/core`: a drag ends by computing
the destination column (→ status) and/or destination time slot (→ scheduled date/time),
optimistically re-rendering, then calling the same `PATCH /api/tasks/{id}` endpoint used by
the edit form. On a rejected response the optimistic change is rolled back and the
error is shown (Principle III). See [Drag-and-drop data flow](#drag-and-drop-data-flow)
below and [quickstart.md](./quickstart.md) for the runnable scenario.

**Backend architecture**: FastAPI app with three layers — `api/` (routers: request
parsing, HTTP status/error mapping), `services/` (duplicate check, conflict check, CRUD
orchestration — all business rules live here per Principle IV), and `models/` (SQLAlchemy
`Task` ORM model + the DB session). Pydantic schemas in `schemas/` validate every
inbound payload before it reaches a service (Principle V). See [data-model.md](./data-model.md).

**API design**: One resource, `Task`, exposed as a standard REST collection —
`GET/POST /api/tasks`, `GET/PATCH/DELETE /api/tasks/{id}` — with a single `PATCH` used for all
updates including drag-and-drop moves (no separate "move" endpoint; Principle VII). Full
request/response shapes, status codes, and the shared error envelope are defined in
[contracts/tasks-api.md](./contracts/tasks-api.md).

**Data model**: A single `Task` entity (id, title, description, scheduled_at, status,
created_at, updated_at) with a unique DB constraint on `scheduled_at` (NULLs excluded)
that makes conflict/duplicate rejection atomic under concurrent writes. Full field list,
constraints, and validation rules in [data-model.md](./data-model.md).

**Validation strategy**: Three layers, all mandatory, none optional: (1) Pydantic schema
validation (types, required fields, date/time format) rejects malformed input with
`422`/`400` before any business logic runs; (2) service-layer checks run in a fixed
order — duplicate check (title + scheduled_at match) first, then scheduling-conflict
check (scheduled_at match regardless of title) — so a request that fails both gets the
more specific "duplicate" error; (3) the DB unique constraint on `scheduled_at` is the
last-resort atomic guard, caught as an `IntegrityError` and translated to the same `409`
conflict response, covering the race window between the service-layer check and the
write (Principle VIII). The frontend performs only non-authoritative UX validation
(e.g., disabling the submit button while a title is empty) — never a duplicate/conflict
decision (Principle I, II, IV).

**Drag-and-drop data flow**: `dnd-kit` drag-end handler → compute `{status?,
scheduled_at?}` patch from the drop target → optimistic local state update → `PATCH
/api/tasks/{id}` with only the changed field(s) → on `2xx`, keep the optimistic state; on
`404/409/422`, revert the task to its pre-drag column/position and surface the returned
error message (Principle III). Because the endpoint and validation path are identical to
a form-based edit, drag-and-drop cannot bypass duplicate/conflict rules by construction
(Principle IV, VIII).

**Error handling**: The backend returns a single JSON error envelope for every failure
(`{"error": {"code", "message", "details"}}`) with a matching HTTP status
(`400`/`404`/`409`/`422`/`500`); the frontend's API client throws a typed `ApiError` on
any non-2xx response, and a shared `ErrorBanner`/toast component renders `error.message`
— the UI never shows a raw stack trace or network exception (FR-016). Full status-code
and error-code table in [contracts/tasks-api.md](./contracts/tasks-api.md).

**Testing strategy**: Backend — `pytest` + FastAPI's `TestClient`, run directly against
the service layer and a real (file-based, per-test) SQLite database, with mandatory
coverage for duplicate rejection, scheduling-conflict rejection (including the
same-title-and-time and different-title-same-time cases), and self-update
non-conflict, per Constitution Principle VI. Frontend — `Vitest` + `React Testing
Library` for component/hook behavior (optimistic update + rollback on rejected
drag), with the API layer mocked. See [quickstart.md](./quickstart.md) for the
end-to-end validation walkthrough that exercises both together.

**Frontend and backend integration**: The two are integrated only through the contract
in [contracts/tasks-api.md](./contracts/tasks-api.md), agreed and documented before any
frontend code calls it (Principle V). During development, the frontend runs against the
real backend on `localhost` (CORS enabled for the Vite dev server origin) — no mock
server is introduced, keeping one source of truth for API behavior (Principle VII).

**Development order**: (1) Data model + migrations + unique constraint; (2) backend
service layer + duplicate/conflict validation with unit tests; (3) REST API routers +
contract tests against `contracts/tasks-api.md`; (4) static board UI against the live
API (create/view/update/delete, no drag yet); (5) drag-and-drop wired to the same
`PATCH` endpoint with optimistic update/rollback; (6) error-handling polish
(`ErrorBanner`, friendly messages for every error code); (7) persistence/refresh and
end-to-end pass through [quickstart.md](./quickstart.md). This order front-loads the
backend rules the constitution treats as non-negotiable (Principles I, II, VI) before
any UI depends on them.

## Technical Context

**Language/Version**: Python 3.12 (backend); JavaScript (ES2022+) with React 18 (frontend, no TypeScript — per explicit requirement)

**Primary Dependencies**: Backend — FastAPI, SQLAlchemy 2.x, Pydantic v2, Uvicorn. Frontend — React 18, Vite, `@dnd-kit/core` (drag-and-drop), native `fetch` (no HTTP client library)

**Storage**: SQLite (file-based relational DB) via SQLAlchemy ORM, with a unique constraint on `Task.scheduled_at`

**Testing**: Backend — `pytest` + FastAPI `TestClient`/`httpx` against a real per-test SQLite DB. Frontend — `Vitest` + `React Testing Library`

**Target Platform**: Web application — any modern browser (frontend) talking to a backend service deployable on Linux/macOS/Windows (no OS-specific dependencies)

**Project Type**: web (frontend + backend detected → Option 2 structure below)

**Performance Goals**: Board view and task mutations respond within ~300ms server-side under light load (tens of concurrent users) — appropriate for a single-team learning-scale app, not a high-throughput production target

**Constraints**: No authentication/authorization (single shared workspace, per spec Assumptions); no offline mode; all task timestamps stored as UTC ISO-8601 and compared at minute granularity (see [research.md](./research.md) for the timezone decision); no recurring tasks or task duration

**Scale/Scope**: Single shared task board, expected low hundreds of tasks; one feature (task CRUD + scheduling + drag-and-drop), five REST endpoints, one data entity

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Design response |
|---|---|---|
| I. Task Integrity | Backend-issued unique ID; duplicate detection backend-authoritative, one consistent rule | UUID/PK generated by DB; duplicate rule (title + scheduled_at) implemented once in `services/`, applied on create AND update; frontend has no duplicate logic |
| II. Scheduling Integrity | Backend validates every create/update for conflicts; clear rejection message + status code | `services/` conflict check (scheduled_at match) on create/update/drag; `409` with task-identifying message; single time-comparison rule (UTC, exact match) reused everywhere |
| III. Drag-and-Drop Integrity | No invalid state via drag; every drag change persisted via backend | Drag end always calls `PATCH /api/tasks/{id}` (same path/validation as forms); optimistic UI rolled back on rejection |
| IV. Separation of Concerns | Frontend/backend independent; business rules in backend only | Frontend limited to `components/`, `hooks/`, `services/api.js`; zero duplicate/conflict logic client-side |
| V. API-First Development | Contract defined before frontend integration; inputs validated; meaningful status/errors | `contracts/tasks-api.md` authored in Phase 1 before any frontend work begins (see Development order); Pydantic validation on every endpoint; shared error envelope |
| VI. Testing and Quality | Automated backend tests for duplicate, conflict, drag-persisted updates | Listed explicitly in Testing strategy and carried into `tasks.md` as release-blocking |
| VII. Simplicity | No unjustified abstractions/dependencies | SQLite (no server to run), native `fetch` (no axios), single `PATCH` endpoint (no separate move endpoint), no auth system |
| VIII. Data Integrity & Consistency | Atomic enforcement of duplicate/conflict checks | Unique DB constraint on `scheduled_at` as last-resort atomic guard behind the service-layer check |

**Result**: PASS — no violations. Complexity Tracking table below is not needed.

**Post-Phase 1 re-check**: After producing `research.md`, `data-model.md`,
`contracts/tasks-api.md`, and `quickstart.md`, the design introduces no new dependency,
service, or abstraction beyond what the table above accounts for (single SQLite DB,
single FastAPI service, single REST resource, no move-specific endpoint). Gate remains
**PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/         # SQLAlchemy Task model + DB session/engine setup
│   ├── schemas/         # Pydantic request/response schemas (input validation)
│   ├── services/         # Business rules: duplicate check, conflict check, task CRUD orchestration
│   ├── api/               # FastAPI routers (tasks.py) — request parsing, status/error mapping
│   └── main.py            # FastAPI app entrypoint, CORS config
└── tests/
    ├── contract/          # Request/response shape + status code tests against contracts/tasks-api.md
    ├── integration/       # Duplicate/conflict/drag-persistence flows against a real SQLite DB
    └── unit/              # Service-layer validation logic in isolation

frontend/
├── src/
│   ├── components/        # TaskCard, TaskColumn, TaskBoard, TaskForm, ErrorBanner
│   ├── pages/              # BoardPage
│   ├── hooks/              # useTasks (state + API calls), useDragAndDrop
│   ├── services/           # api.js — REST client (fetch wrapper, typed ApiError)
│   └── main.jsx            # App entrypoint
└── tests/
    ├── unit/               # Component/hook tests (React Testing Library)
    └── integration/        # Board interaction flows (drag, optimistic update + rollback) with mocked API
```

**Structure Decision**: Option 2 (web application) — the feature spans an independently
deployable `frontend/` (React) and `backend/` (FastAPI) with no shared source, matching
Constitution Principle IV (Separation of Concerns). All cross-boundary communication
goes through the REST contract in `contracts/tasks-api.md`.

## Complexity Tracking

*No entries — the Constitution Check above passed without violations. This project
deliberately avoids introducing anything (an ORM abstraction layer beyond SQLAlchemy's
own, a state-management library, a second backend service, etc.) that isn't required by
the functional requirements, per Principle VII (Simplicity).*
