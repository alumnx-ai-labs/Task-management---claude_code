<!--
Sync Impact Report
===================
Version change: [TEMPLATE] → 1.0.0 (initial ratification)

Modified principles: N/A (first adoption from unfilled template)

Added sections:
  - Core Principles I–VIII
    I. Task Integrity
    II. Scheduling Integrity
    III. Drag-and-Drop Interaction Integrity
    IV. Separation of Concerns
    V. API-First Development
    VI. Testing and Quality
    VII. Simplicity
    VIII. Data Integrity & Consistency (added — not explicitly requested by user,
          proposed as an important engineering principle; see rationale below)
  - Technology Stack & Architecture (SECTION_2)
  - Development Workflow & Quality Gates (SECTION_3)
  - Governance

Removed sections: N/A

Deferred / TODO placeholders: None. RATIFICATION_DATE and LAST_AMENDED_DATE are
set to the date this constitution was drafted and adopted (2026-08-29), since no
prior ratified version of this document existed.

Rationale for Principle VIII (Data Integrity & Consistency):
The user's principles (Task Integrity, Scheduling Integrity) both depend on the
backend being able to make atomic, race-condition-free decisions when two
requests arrive close together (e.g., two duplicate-creation requests, or two
scheduling requests for the same slot). Without an explicit principle requiring
transactional/atomic enforcement at the data layer, "backend must validate"
could be implemented in a way that is still vulnerable to race conditions. This
principle closes that gap.

Templates requiring follow-up:
  - .specify/templates/plan-template.md — ⚠ pending manual review to confirm its
    Constitution Check section references these 8 principles by name.
  - .specify/templates/spec-template.md — ⚠ pending manual review for consistency
    with duplicate/scheduling terminology.
  - .specify/templates/tasks-template.md — ⚠ pending manual review to ensure
    task categories reference backend-first validation and test coverage rules.
  (Not modified by this command — scope is limited to the constitution itself.)
-->

# Task Management Application Constitution

## Core Principles

### I. Task Integrity
Every task MUST have a unique, backend-issued identity (e.g., a UUID or database
primary key) that is never reused. Duplicate tasks MUST NOT be created under any
circumstance. Duplicate detection MUST be enforced in the backend as the
authoritative check — the frontend MAY offer client-side hints (e.g., a warning
before submit) but MUST NOT be relied upon as the source of truth, since it can
be bypassed, disabled, or race against concurrent clients. The definition of
"duplicate" (e.g., matching title + scheduled time, or another explicit key)
MUST be documented in the backend's API contract and applied consistently
across every creation and update code path — there MUST NOT be a second,
divergent duplicate-detection rule anywhere else in the system.

**Rationale**: Identity and uniqueness are the foundation a task list is built
on; if two clients or two rapid requests can each believe they "won," the data
becomes untrustworthy and every downstream feature (scheduling, drag-and-drop,
counts) inherits the corruption.

### II. Scheduling Integrity
Two tasks MUST NOT be scheduled for the same time. The backend MUST validate
every create and update request for scheduling conflicts before persisting it;
client-side time-picker restrictions are a UX convenience only and MUST NOT be
treated as validation. A request that would create a conflict MUST be rejected
with a clear, actionable error message (what conflicts, and with which existing
task) and a meaningful HTTP status code (e.g., `409 Conflict`). Time comparison
logic (time zones, granularity, inclusive/exclusive boundaries) MUST be defined
once in the backend and reused everywhere a scheduling decision is made —
frontend, backend, and tests MUST all reason about time the same way.

**Rationale**: Scheduling conflicts are a correctness issue, not a display
issue; a project meant to teach end-to-end SpecKit development needs this rule
enforced where it can actually be trusted — server-side — with feedback precise
enough for a user to fix the conflict.

### III. Drag-and-Drop Interaction Integrity
Tasks MUST support drag-and-drop interactions for rescheduling and/or status
changes. A drag-and-drop interaction MUST NOT be allowed to produce an invalid
task state (e.g., dropping onto an occupied time slot, or into a status the
task cannot legally transition to) — the same rules defined in Principles I and
II apply to drag-and-drop moves exactly as they apply to form-based edits.
Every change made via drag-and-drop MUST be persisted through the backend API;
optimistic UI updates are permitted for responsiveness, but MUST be rolled back
in the UI if the backend rejects the change, and MUST NOT be treated as
committed until the backend confirms success.

**Rationale**: Drag-and-drop is a convenience layer over the same state
transitions as any other edit; letting it skip backend validation would create
a second, unguarded path to the same integrity problems Principles I and II
exist to prevent.

### IV. Separation of Concerns
The React frontend and the Python backend MUST remain independently
deployable and independently testable, communicating only through the defined
REST API — the frontend MUST NOT embed business rules (duplicate detection,
scheduling conflict resolution, valid state transitions) that would allow it to
diverge from the backend's decisions. Business rules MUST be implemented
primarily in the backend, which is the single source of truth for whether an
action is valid. The frontend's responsibility is user interaction,
presentation, optimistic feedback, and calling the API correctly.

**Rationale**: Keeping business logic in one place (the backend) is what makes
Principles I–III enforceable at all; if the frontend can independently decide
what's valid, the two layers will eventually disagree.

### V. API-First Development
Backend REST API endpoints (resource shapes, request/response payloads, status
codes, and error formats) MUST be defined and documented before frontend
integration work begins against them. Every API endpoint MUST validate its
inputs (types, required fields, value constraints) and MUST reject invalid
input rather than attempting to silently coerce or ignore it. Every response
MUST use a meaningful, correct HTTP status code and, on failure, a clear
human-readable error message that identifies what was wrong.

**Rationale**: A clearly specified API contract is what lets the frontend and
backend be built and tested independently (Principle IV) and is what makes the
rejection messages required by Principles I and II possible in the first
place.

### VI. Testing and Quality
Critical business rules MUST have automated tests, and these are treated as
release-blocking, non-negotiable coverage: duplicate task prevention (Principle
I), scheduling conflict detection (Principle II), and task updates performed
through drag-and-drop (Principle III). Tests for these rules MUST exercise the
backend directly (not only through the UI), since the backend is the
authoritative enforcement point. Additional tests are encouraged wherever they
add confidence, but these three areas MUST NOT ship uncovered.

**Rationale**: These three behaviors are exactly the ones a duplicate, a double
booking, or a corrupted drag-and-drop move would violate silently; automated
tests are what keep a small learning project honest as it grows.

### VII. Simplicity
Prefer simple, understandable solutions over clever or speculative ones.
Avoid unnecessary abstractions, layers, or dependencies that do not serve a
concrete, current requirement of this application. New abstractions,
libraries, or architectural layers MUST be justified by a real need, not by
anticipated future needs. This project is explicitly intended as an end-to-end
learning vehicle for SpecKit-driven development, and its design MUST stay
approachable enough to serve that purpose.

**Rationale**: Complexity introduced "just in case" is the most common way a
learning project stops being learnable; every added moving part must earn its
place.

### VIII. Data Integrity & Consistency
The backend's database MUST be the single source of truth for task state.
Operations that enforce Principles I and II (duplicate detection, scheduling
conflict checks) MUST be atomic with respect to the write they guard — for
example, using a database transaction, unique constraint, or equivalent
mechanism — so that two near-simultaneous requests cannot both pass validation
and both be persisted. No code path may leave a task in a partially written or
inconsistent state (e.g., a moved task recorded as removed from its old slot
but not written to its new one).

**Rationale**: "Validate in the backend" (Principles I and II) is only a real
guarantee if the validation and the write cannot be split apart by a race
condition; this principle makes that guarantee explicit rather than assumed.

## Technology Stack & Architecture

- **Frontend**: React. Responsible for rendering task views, drag-and-drop
  interactions, forms, and optimistic UI feedback; MUST call the backend REST
  API for any operation that creates, reads, updates, or deletes task data.
- **Backend**: Python. Responsible for all business rules, persistence, and
  validation described in Principles I, II, V, and VIII; exposes its
  functionality exclusively through the REST API.
- **Communication**: REST APIs over HTTP(S) using JSON request/response
  bodies are the only integration point between frontend and backend. The
  frontend MUST NOT access the backend's database or internal modules
  directly.
- Technology choices beyond this stack (specific frameworks, libraries, the
  database engine) are implementation details left to the plan/design phase,
  and MUST be chosen in line with Principle VII (Simplicity) — favor
  well-established, minimal-dependency options appropriate for a learning
  project.

## Development Workflow & Quality Gates

- API contracts (endpoint, request/response shape, status codes, error
  format) MUST exist — at minimum as an agreed specification — before the
  corresponding frontend feature is implemented against it (Principle V).
- A pull request or change that touches duplicate detection, scheduling
  conflict logic, or drag-and-drop persistence MUST include or update the
  automated tests required by Principle VI before it can be merged.
- Code review MUST verify that business rules being added or changed live in
  the backend, not the frontend (Principle IV), and that new dependencies or
  abstractions are justified (Principle VII).
- Backend input validation and error responses MUST be verified (manually or
  via tests) to return meaningful status codes and messages before a feature
  is considered done (Principle V).

## Governance

This constitution supersedes any conflicting practice, informal convention, or
prior undocumented decision in this project. All specs, plans, and task lists
produced by the SpecKit workflow MUST be checked against these principles;
any deviation MUST be explicitly justified in the relevant plan's Complexity
Tracking (or equivalent) section rather than silently introduced.

**Amendment procedure**: Amendments are proposed by editing this file, stating
the change and its rationale, and re-running the constitution workflow so the
Sync Impact Report and version are regenerated. A change is adopted once the
project maintainer(s) accept the updated file.

**Versioning policy**: This constitution follows semantic versioning:
- **MAJOR** — a principle is removed or redefined in a backward-incompatible
  way (e.g., relaxing a MUST to a SHOULD, or removing an enforcement
  requirement).
- **MINOR** — a new principle or section is added, or existing guidance is
  materially expanded.
- **PATCH** — wording clarifications, typo fixes, or other non-semantic
  refinements.

**Compliance review**: Every feature's plan MUST include a Constitution Check
step confirming alignment with these principles before implementation begins,
and again before the feature is marked complete. Reviewers and implementers
should treat repeated or systemic violations of a principle as a signal that
either the implementation or the constitution itself needs to change —
handled through this same amendment procedure, not through silent exceptions.

**Version**: 1.0.0 | **Ratified**: 2026-08-29 | **Last Amended**: 2026-08-29
