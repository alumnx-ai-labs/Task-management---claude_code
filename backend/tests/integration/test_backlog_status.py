def test_task_created_with_backlog_status_round_trips_through_list(client):
    created = client.post("/api/tasks", json={"title": "Someday idea", "status": "backlog"})
    assert created.status_code == 201
    assert created.json()["status"] == "backlog"

    tasks = client.get("/api/tasks").json()["tasks"]
    matching = next(t for t in tasks if t["id"] == created.json()["id"])
    assert matching["status"] == "backlog"


def test_duplicate_detection_applies_to_backlog_tasks(client):
    first = client.post(
        "/api/tasks",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z", "status": "backlog"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/tasks",
        json={"title": "team sync", "scheduled_at": "2026-09-03T14:30:00Z", "status": "todo"},
    )

    assert second.status_code == 409
    assert second.json()["error"]["code"] == "DUPLICATE_TASK"


def test_scheduling_conflict_applies_to_backlog_tasks(client):
    first = client.post(
        "/api/tasks",
        json={"title": "Busy slot", "scheduled_at": "2026-09-03T14:30:00Z", "status": "todo"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/tasks",
        json={
            "title": "Someday idea",
            "scheduled_at": "2026-09-03T14:30:00Z",
            "status": "backlog",
        },
    )

    assert second.status_code == 409
    assert second.json()["error"]["code"] == "SCHEDULING_CONFLICT"
