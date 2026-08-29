import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from src.db import Base

STATUSES = ("backlog", "todo", "in_progress", "done")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UTCDateTime(TypeDecorator):
    """SQLite has no native timezone-aware storage — it silently drops tzinfo on
    read-back. Since every datetime in this app is UTC by design (research.md §4),
    this type re-attaches UTC on the way out so API responses are always
    unambiguous ISO-8601 (e.g. "...+00:00"), not a bare timestamp a client could
    misinterpret as local time."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Unique (excluding NULL, which SQL unique indexes treat as distinct per row)
    # so unscheduled tasks never conflict with each other. This is the DB-level
    # atomicity backstop for the duplicate/conflict checks (Constitution Principle VIII).
    scheduled_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime, nullable=True, unique=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="todo")
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )
