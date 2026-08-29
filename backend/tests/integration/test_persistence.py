from sqlalchemy.orm import sessionmaker

from src.schemas.task import TaskCreate
from src.services import task_service


def test_created_task_survives_a_fresh_session(db_engine):
    SessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)

    session_one = SessionLocal()
    created = task_service.create_task(session_one, TaskCreate(title="Persist me"))
    task_id = created.id
    session_one.close()

    # A brand-new session against the same underlying file simulates the
    # backend having restarted and reconnected to the database (FR-014).
    session_two = SessionLocal()
    reloaded = task_service.get_task(session_two, task_id)
    session_two.close()

    assert reloaded is not None
    assert reloaded.title == "Persist me"
    assert reloaded.id == task_id
