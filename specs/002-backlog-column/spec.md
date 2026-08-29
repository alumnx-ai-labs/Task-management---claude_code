# Feature Specification: Backlog Status Column

**Feature Branch**: `002-backlog-column`

**Created**: 2026-08-29

**Status**: Draft

**Input**: User description: "implement a new vertical column backlog similar to the todo, progress, done. the place of the backlog board should be before the todo."

This feature extends the existing Task Management Application (see `specs/001-task-management/`) by adding one additional status/column — it does not change the combined status/time board design, drag-and-drop mechanics, or any business rule established there; it only adds a fourth status value that those existing rules apply to.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See Backlog as the First Column (Priority: P1)

A user opens the board and sees a new "Backlog" column positioned to the left of "To Do", so the column order reads Backlog, To Do, In Progress, Done. Any task already assigned Backlog status appears there, organized the same way as tasks in any other column (ordered by scheduled date/time, with an "Unscheduled" grouping).

**Why this priority**: The column has to exist and be positioned correctly before it's useful for anything else — this is the minimum visible slice of the feature.

**Independent Test**: Load the board and confirm a "Backlog" column renders first (before "To Do"), with the same layout conventions (scheduled/unscheduled grouping) as the existing columns.

**Acceptance Scenarios**:

1. **Given** the board is open, **When** a user views it, **Then** four columns are visible in this order: Backlog, To Do, In Progress, Done.
2. **Given** a task has Backlog status, **When** the user views the board, **Then** that task appears in the Backlog column, grouped by scheduled date/time or under "Unscheduled" exactly as it would in any other column.
3. **Given** no task currently has Backlog status, **When** the user views the board, **Then** the Backlog column is present but empty — it is never auto-populated with existing tasks.

---

### User Story 2 - Assign a Task To or From Backlog (Priority: P2)

A user creates a new task directly into Backlog, or moves an existing task into or out of Backlog — either by editing its status or by dragging it into/out of the Backlog column — using the same mechanisms already available for To Do, In Progress, and Done.

**Why this priority**: Being able to see the column (User Story 1) delivers value on its own once existing data can be assigned to it manually elsewhere; being able to assign tasks to it through the UI is the next increment that makes it fully usable.

**Independent Test**: Create a task with status Backlog directly; separately, edit an existing To Do task's status to Backlog; separately, drag a task into and out of the Backlog column. Confirm all three work exactly as the equivalent action does for any other status, including duplicate/conflict rejection and drag rollback on an invalid drop.

**Acceptance Scenarios**:

1. **Given** the task creation form, **When** a user selects "Backlog" as the status and submits, **Then** the task is created with Backlog status and appears in the Backlog column.
2. **Given** an existing task in any status, **When** a user edits it and changes its status to Backlog, **Then** the task moves to the Backlog column, subject to the same duplicate/scheduling-conflict validation as any other update.
3. **Given** a task in the Backlog column, **When** a user drags it into another column (To Do, In Progress, or Done), **Then** its status updates accordingly, the same way dragging between any other two columns does.
4. **Given** a task in another column, **When** a user drags it into the Backlog column onto an already-occupied scheduled time, **Then** the move is rejected with a scheduling-conflict error and the task visually returns to its original position — identical to a rejected drag into any other column.

---

### Edge Cases

- What happens to tasks that existed before this feature was introduced? (They keep their current status; Backlog starts empty and nothing is automatically moved into it.)
- Can a task move directly from Backlog to Done without passing through To Do or In Progress? (Yes — there is no restricted status workflow; this matches the existing "no status-based exemption from any rule" behavior for all statuses.)
- What happens when a task is dragged into Backlog's "Unscheduled" area versus its scheduled area? (Same behavior as any other column: the unscheduled area clears the task's schedule, the scheduled area assigns/keeps one.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support "Backlog" as a valid task status, in addition to the existing To Do, In Progress, and Done statuses.
- **FR-002**: The system MUST display the Backlog column as the leftmost column on the board — the column order MUST be Backlog, To Do, In Progress, Done.
- **FR-003**: The system MUST allow a task to be created directly with Backlog status, and allow any existing task's status to be changed to or from Backlog, exactly as with any other status.
- **FR-004**: The system MUST support dragging a task into or out of the Backlog column, applying the same status/schedule update behavior and destination validation (including scheduling-conflict rejection) already defined for drag-and-drop between the existing columns.
- **FR-005**: The system MUST continue to default a newly created task's status to "To Do" when no status is explicitly chosen — introducing Backlog MUST NOT change this existing default.
- **FR-006**: The system MUST apply all existing duplicate-detection and scheduling-conflict rules to Backlog tasks identically to tasks in any other status, with no status-based exemption.
- **FR-007**: The system MUST organize tasks within the Backlog column the same way as every other column — ordered by scheduled date/time, with an "Unscheduled" grouping for tasks that have no schedule.

### Key Entities

- **Task**: No new entity or field is introduced. The existing Task's status attribute gains one additional valid value ("Backlog"), alongside To Do, In Progress, and Done.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of tasks assigned Backlog status appear in the Backlog column, which is always displayed as the first (leftmost) column on the board.
- **SC-002**: A user can assign a task to Backlog — at creation or via update — in the same number of steps already required to assign any other status.
- **SC-003**: A user can drag a task into or out of Backlog with the same success/rejection/rollback behavior already guaranteed for drag-and-drop between the existing columns, verified across both a successful move and a rejected (conflicting) move.
- **SC-004**: Introducing this feature does not change the status of any task that existed beforehand — verified by confirming pre-existing tasks remain in their original column after the feature ships.

## Assumptions

- The default status for a newly created task remains "To Do"; Backlog is only assigned when a user explicitly selects it (via the status field) or drags a task into it. This is a deliberate choice to avoid changing any existing behavior beyond adding the new column.
- No new business rules, fields, or entities are introduced. Backlog is purely an additional status/column value that inherits every existing rule (duplicate detection, scheduling-conflict detection, drag-and-drop validation, persistence, error handling) already defined for the Task Management Application.
- This feature builds directly on the existing combined status/time board (`specs/001-task-management/`) and does not alter its layout model, time-comparison rules, or API contract shape beyond widening the set of valid status values.
