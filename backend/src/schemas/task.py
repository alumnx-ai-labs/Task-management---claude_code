from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator

Status = Literal["todo", "in_progress", "done"]


def _validate_title(v: str) -> str:
    trimmed = v.strip()
    if not trimmed:
        raise ValueError("title must not be blank")
    return trimmed


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Status = "todo"

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        return _validate_title(v)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[Status] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_title(v)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Status
    created_at: datetime
    updated_at: datetime


class TaskList(BaseModel):
    tasks: list[TaskRead]
