# Phase 0 Research: Task Management Application

All items below were resolvable from the spec, the constitution, and the user's explicit
technology constraints (React/JavaScript frontend, Python/REST backend) — no items were
left as `NEEDS CLARIFICATION` in the Technical Context. Each decision favors the fewest
moving parts that satisfy the spec's functional requirements, per Constitution Principle
VII (Simplicity).

## 1. Backend web framework

- **Decision**: FastAPI
- **Rationale**: Built-in request validation via Pydantic satisfies FR-015 ("validate
  all task input... reject invalid input with a specific, actionable validation error")
  with no extra library. Automatic OpenAPI schema generation directly supports
  Constitution Principle V (API-First Development) — the contract in
  `contracts/tasks-api.md` can be cross-checked against the generated schema. Async-
  capable but not required to be used as such for this scale.
- **Alternatives considered**: Flask (would require adding a separate validation library
  such as `marshmallow` or `pydantic` by hand — more moving parts for the same outcome);
  Django (its ORM/admin/auth machinery is far more than this single-entity, no-auth
  feature needs — violates Simplicity).

## 2. Persistence

- **Decision**: SQLite via SQLAlchemy 2.x ORM, one file-based database, a unique
  constraint on `Task.scheduled_at`.
- **Rationale**: No separate database server to install/run — appropriate for a
  learning-scale, single-shared-workspace app (per spec Assumptions: no multi-tenant,
  no auth). SQLAlchemy gives a real unique-constraint/transaction mechanism, which
  Constitution Principle VIII requires for atomic duplicate/conflict enforcement — a
  plain-file or in-memory store would not provide this without reimplementing locking.
  Most SQL databases (SQLite included) treat multiple `NULL`s as distinct under a unique
  index, so unscheduled tasks (`scheduled_at IS NULL`) are never treated as conflicting
  with each other — matching FR-011/Edge Cases.
- **Alternatives considered**: PostgreSQL (real option for production, but adds a
  service dependency with no benefit at this scale); in-memory dict/list (rejected —
  Principle VIII requires atomic, constraint-backed writes, and data would not survive
  a server restart, violating FR-014 persistence).

## 3. Duplicate vs. scheduling-conflict validation ordering

- **Decision**: On create/update, run the duplicate check (title + scheduled_at match)
  before the scheduling-conflict check (scheduled_at match regardless of title). Return
  on the first failure.
- **Rationale**: Every duplicate (by FR-010's definition) is also, by definition, a
  scheduling conflict (FR-011 forbids *any* two tasks sharing a scheduled_at, regardless
  of title) — so a title+time collision would satisfy both rules. Checking duplicate
  first produces the more specific, more useful error message ("this looks like the
  same task already on the board" vs. the more generic "that time is taken"), matching
  FR-016's requirement for clear, specific errors, without changing what gets rejected.
- **Alternatives considered**: Conflict-first ordering (rejected — every title-matching
  case would then report the generic conflict error, hiding the more actionable
  duplicate signal); running both checks and combining messages (rejected — added
  complexity for a case that already has a single unambiguous first cause).

## 4. Timezone / date-time handling

- **Decision**: Store `scheduled_at` as UTC (ISO-8601) in the database. The frontend
  converts to/from the browser's local timezone only for display and input; all
  conflict/duplicate comparisons happen server-side on the stored UTC value, compared
  for exact equality to the minute (per the FR-012 clarification: no duration, exact
  match).
- **Rationale**: A single, server-side source of truth for "same time" avoids the
  classic bug where frontend and backend disagree about time-zone offsets (Constitution
  Principle II: "Time comparison logic... MUST be defined once in the backend and reused
  everywhere"). The spec's single-shared-workspace assumption means no per-user timezone
  preference needs to be modeled.
- **Alternatives considered**: Storing local time with a timezone-offset field (rejected
  — adds a field and normalization logic the spec doesn't call for); comparing at
  second/millisecond precision (rejected — FR-012 explicitly says "to the minute").

## 5. Drag-and-drop library (frontend)

- **Decision**: `@dnd-kit/core`
- **Rationale**: Actively maintained, accessible (keyboard + screen-reader support out
  of the box), and unopinionated about layout — fits the combined status-column +
  time-ordered board from the Clarifications without fighting a more rigid library.
- **Alternatives considered**: `react-beautiful-dnd` (rejected — officially deprecated,
  no longer maintained); building drag-and-drop from raw HTML5 DnD events (rejected —
  significantly more code to reach the same accessible, cross-browser behavior;
  violates Simplicity by hand-rolling what a small, well-established library already
  provides).

## 6. Frontend HTTP client

- **Decision**: Native `fetch`, wrapped in a small `services/api.js` module that throws
  a typed `ApiError` on non-2xx responses.
- **Rationale**: `fetch` is available in all supported browsers with no dependency; a
  thin wrapper is enough to centralize the error envelope → `ApiError` translation
  needed for FR-016 (frontend must present backend errors in a user-friendly form).
- **Alternatives considered**: `axios` (rejected — adds a dependency for interceptor/
  convenience features this feature doesn't need; Principle VII).

## 7. Testing tools

- **Decision**: Backend — `pytest` + FastAPI's `TestClient` (built on `httpx`) against a
  real per-test SQLite database (fresh file or in-memory DB per test run). Frontend —
  `Vitest` (pairs natively with Vite, no separate test-runner config) + `React Testing
  Library`.
- **Rationale**: Constitution Principle VI requires the duplicate/conflict/drag-and-drop
  tests to exercise the backend directly rather than only through the UI — `TestClient`
  against a real DB (not a mock) is the most direct way to prove the unique constraint
  and service-layer checks actually work together.
- **Alternatives considered**: Mocking the DB layer in backend tests (rejected — would
  not verify the Principle VIII atomicity guarantee, which depends on the real unique
  constraint); Cypress/Playwright end-to-end tests (not ruled out for later, but not
  required to satisfy Principle VI's minimum bar, and adds a heavier tool than this
  feature's scope needs right now).
