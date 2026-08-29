import re
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.errors import DuplicateTaskError, SchedulingConflictError, TaskNotFoundError
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskUpdate

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_title(title: str) -> str:
    """Case-insensitive, whitespace-collapsed title key used for duplicate matching (FR-010)."""
    return _WHITESPACE_RE.sub(" ", title.strip()).lower()


def _truncate_to_minute(value: datetime | None) -> datetime | None:
    """Sub-minute precision is truncated (not rounded) before any comparison or storage (FR-012)."""
    if value is None:
        return None
    return value.replace(second=0, microsecond=0)


def _find_conflicting_task(
    db: Session, scheduled_at: datetime | None, exclude_id: str | None
) -> Task | None:
    if scheduled_at is None:
        return None
    stmt = select(Task).where(Task.scheduled_at == scheduled_at)
    if exclude_id is not None:
        stmt = stmt.where(Task.id != exclude_id)
    return db.execute(stmt).scalars().first()


def _ensure_schedule_is_free(
    db: Session, title: str, scheduled_at: datetime | None, exclude_id: str | None
) -> None:
    """Raises DuplicateTaskError (FR-009/FR-010) or SchedulingConflictError (FR-011)
    if `scheduled_at` is already occupied. A duplicate is a conflict with a matching
    title, so the same lookup serves both rules (research.md §3): at most one other
    task can ever hold a given `scheduled_at` at a time, so `.first()` is sufficient.
    `exclude_id` excludes the task's own record so it never conflicts with itself
    (FR-010, FR-013)."""
    existing = _find_conflicting_task(db, scheduled_at, exclude_id)
    if existing is None:
        return
    if _normalize_title(existing.title) == _normalize_title(title):
        raise DuplicateTaskError(
            f'A task titled "{existing.title}" is already scheduled for that date and time.',
            {"conflicting_task_id": existing.id},
        )
    raise SchedulingConflictError(
        f"Another task (\"{existing.title}\") is already scheduled for that date and time.",
        {"conflicting_task_id": existing.id},
    )


def create_task(db: Session, data: TaskCreate) -> Task:
    scheduled_at = _truncate_to_minute(data.scheduled_at)
    _ensure_schedule_is_free(db, data.title, scheduled_at, exclude_id=None)

    task = Task(
        title=data.title,
        description=data.description,
        scheduled_at=scheduled_at,
        status=data.status,
    )
    db.add(task)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # The pre-check above passed, but a concurrent request committed first
        # (Constitution Principle VIII) — re-check to report the correct, specific
        # error rather than a generic failure.
        _ensure_schedule_is_free(db, data.title, scheduled_at, exclude_id=None)
        raise
    db.refresh(task)
    return task


def list_tasks(db: Session) -> list[Task]:
    return list(db.execute(select(Task).order_by(Task.created_at)).scalars())


def get_task(db: Session, task_id: str) -> Task | None:
    return db.get(Task, task_id)


def update_task(db: Session, task_id: str, data: TaskUpdate) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise TaskNotFoundError(f"No task found with id {task_id}.")

    updates = data.model_dump(exclude_unset=True)
    new_title = updates.get("title", task.title)
    new_scheduled_at = _truncate_to_minute(
        updates["scheduled_at"] if "scheduled_at" in updates else task.scheduled_at
    )

    # Applies identically regardless of the task's current or new status (FR-018) —
    # there is no status-based exemption anywhere in this function.
    _ensure_schedule_is_free(db, new_title, new_scheduled_at, exclude_id=task.id)

    for field, value in updates.items():
        setattr(task, field, _truncate_to_minute(value) if field == "scheduled_at" else value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        _ensure_schedule_is_free(db, new_title, new_scheduled_at, exclude_id=task.id)
        raise
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: str) -> None:
    task = db.get(Task, task_id)
    if task is None:
        raise TaskNotFoundError(f"No task found with id {task_id}.")
    db.delete(task)
    db.commit()
