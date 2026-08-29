def test_duplicate_same_title_and_time_is_rejected(client):
    first = client.post(
        "/api/tasks",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/tasks",
        json={"title": "team sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    )

    assert second.status_code == 409
    assert second.json()["error"]["code"] == "DUPLICATE_TASK"


def test_same_title_different_time_is_not_a_duplicate(client):
    first = client.post(
        "/api/tasks",
        json={"title": "Follow up", "scheduled_at": "2026-09-03T14:30:00Z"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/tasks",
        json={"title": "Follow up", "scheduled_at": "2026-09-04T09:00:00Z"},
    )

    assert second.status_code == 201


def test_same_title_both_unscheduled_is_not_a_duplicate(client):
    first = client.post("/api/tasks", json={"title": "Backlog item"})
    assert first.status_code == 201

    second = client.post("/api/tasks", json={"title": "Backlog item"})

    assert second.status_code == 201


def test_internal_whitespace_is_collapsed_for_duplicate_comparison(client):
    first = client.post(
        "/api/tasks",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/tasks",
        json={"title": "Team   Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    )

    assert second.status_code == 409
    assert second.json()["error"]["code"] == "DUPLICATE_TASK"
