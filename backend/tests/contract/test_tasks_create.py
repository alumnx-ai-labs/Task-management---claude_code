def test_create_task_title_only_success(client):
    response = client.post("/api/tasks", json={"title": "Write report"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write report"
    assert body["description"] is None
    assert body["scheduled_at"] is None
    assert body["status"] == "todo"
    assert body["id"]


def test_create_task_full_fields_success(client):
    response = client.post(
        "/api/tasks",
        json={
            "title": "Team sync",
            "description": "Weekly status check-in",
            "scheduled_at": "2026-09-03T14:30:00Z",
            "status": "in_progress",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Team sync"
    assert body["description"] == "Weekly status check-in"
    assert body["status"] == "in_progress"
    assert body["scheduled_at"].startswith("2026-09-03T14:30:00")


def test_create_task_missing_title_returns_422(client):
    response = client.post("/api/tasks", json={"description": "no title here"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_create_task_whitespace_only_title_returns_422(client):
    response = client.post("/api/tasks", json={"title": "   "})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_task_ids_are_distinct(client):
    first = client.post("/api/tasks", json={"title": "Task A"}).json()
    second = client.post("/api/tasks", json={"title": "Task B"}).json()

    assert first["id"] != second["id"]


def test_create_task_with_backlog_status_succeeds(client):
    response = client.post("/api/tasks", json={"title": "Someday idea", "status": "backlog"})

    assert response.status_code == 201
    assert response.json()["status"] == "backlog"
