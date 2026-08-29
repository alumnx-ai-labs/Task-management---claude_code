def test_done_task_can_still_be_rescheduled(client):
    created = client.post(
        "/api/tasks",
        json={"title": "Ship release", "status": "done", "scheduled_at": "2026-09-03T14:30:00Z"},
    ).json()

    response = client.patch(
        f"/api/tasks/{created['id']}",
        json={"scheduled_at": "2026-09-05T10:00:00Z"},
    )

    assert response.status_code == 200
    assert response.json()["scheduled_at"].startswith("2026-09-05T10:00:00")


def test_done_task_is_still_rejected_for_scheduling_conflict(client):
    client.post(
        "/api/tasks",
        json={"title": "Busy slot", "scheduled_at": "2026-09-03T14:30:00Z"},
    )
    done_task = client.post(
        "/api/tasks",
        json={"title": "Ship release", "status": "done"},
    ).json()

    response = client.patch(
        f"/api/tasks/{done_task['id']}",
        json={"scheduled_at": "2026-09-03T14:30:00Z"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "SCHEDULING_CONFLICT"


def test_done_task_is_still_rejected_as_a_duplicate(client):
    client.post(
        "/api/tasks",
        json={"title": "Ship release", "scheduled_at": "2026-09-03T14:30:00Z"},
    )

    response = client.post(
        "/api/tasks",
        json={"title": "Ship release", "scheduled_at": "2026-09-03T14:30:00Z", "status": "done"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_TASK"
