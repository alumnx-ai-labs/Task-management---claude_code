from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db import get_db
from src.schemas.task import TaskCreate, TaskList, TaskRead, TaskUpdate
from src.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskList)
def list_tasks(db: Session = Depends(get_db)) -> TaskList:
    tasks = task_service.list_tasks(db)
    return TaskList(tasks=[TaskRead.model_validate(t) for t in tasks])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskRead)
def create_task(data: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    task = task_service.create_task(db, data)
    return TaskRead.model_validate(task)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: str, data: TaskUpdate, db: Session = Depends(get_db)) -> TaskRead:
    task = task_service.update_task(db, task_id, data)
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)) -> None:
    task_service.delete_task(db, task_id)
