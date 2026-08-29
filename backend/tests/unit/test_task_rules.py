from datetime import datetime, timezone

import pytest

from src.api.errors import DuplicateTaskError, SchedulingConflictError
from src.models.task import Task
from src.services import task_service


def test_normalize_title_trims_collapses_whitespace_and_lowercases():
    assert task_service._normalize_title("  Team   Sync  ") == "team sync"
    assert task_service._normalize_title("Team Sync") == task_service._normalize_title(
        "team   sync"
    )


def test_truncate_to_minute_drops_seconds_and_microseconds():
    value = datetime(2026, 9, 3, 14, 30, 45, 123456, tzinfo=timezone.utc)

    truncated = task_service._truncate_to_minute(value)

    assert truncated == datetime(2026, 9, 3, 14, 30, 0, tzinfo=timezone.utc)


def test_truncate_to_minute_passes_through_none():
    assert task_service._truncate_to_minute(None) is None


def test_ensure_schedule_is_free_raises_duplicate_for_matching_title(db_engine):
    from sqlalchemy.orm import Session

    scheduled_at = datetime(2026, 9, 3, 14, 30, tzinfo=timezone.utc)
    with Session(db_engine) as db:
        existing = Task(title="Team Sync", scheduled_at=scheduled_at)
        db.add(existing)
        db.commit()

        with pytest.raises(DuplicateTaskError):
            task_service._ensure_schedule_is_free(db, "team sync", scheduled_at, exclude_id=None)


def test_ensure_schedule_is_free_raises_conflict_for_different_title(db_engine):
    from sqlalchemy.orm import Session

    scheduled_at = datetime(2026, 9, 3, 14, 30, tzinfo=timezone.utc)
    with Session(db_engine) as db:
        existing = Task(title="Team Sync", scheduled_at=scheduled_at)
        db.add(existing)
        db.commit()

        with pytest.raises(SchedulingConflictError):
            task_service._ensure_schedule_is_free(
                db, "Design review", scheduled_at, exclude_id=None
            )


def test_ensure_schedule_is_free_excludes_own_id(db_engine):
    from sqlalchemy.orm import Session

    scheduled_at = datetime(2026, 9, 3, 14, 30, tzinfo=timezone.utc)
    with Session(db_engine) as db:
        existing = Task(title="Team Sync", scheduled_at=scheduled_at)
        db.add(existing)
        db.commit()

        # Should not raise: the only match is the task's own record.
        task_service._ensure_schedule_is_free(
            db, "Team Sync", scheduled_at, exclude_id=existing.id
        )
