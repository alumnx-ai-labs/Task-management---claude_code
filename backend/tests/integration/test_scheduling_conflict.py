def test_different_title_same_time_is_a_scheduling_conflict(client):
    first = client.post(
        "/api/tasks",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/tasks",
        json={"title": "Design review", "scheduled_at": "2026-09-03T14:30:00Z"},
    )

    assert second.status_code == 409
    body = second.json()
    assert body["error"]["code"] == "SCHEDULING_CONFLICT"
    assert body["error"]["details"]["conflicting_task_id"] == first.json()["id"]


def test_sub_minute_precision_is_truncated_before_comparison(client):
    first = client.post(
        "/api/tasks",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    )
    assert first.status_code == 201

    # Same minute, different seconds — must still be treated as the same time (FR-012).
    second = client.post(
        "/api/tasks",
        json={"title": "Design review", "scheduled_at": "2026-09-03T14:30:45Z"},
    )

    assert second.status_code == 409
    assert second.json()["error"]["code"] == "SCHEDULING_CONFLICT"


def test_different_time_is_not_a_conflict(client):
    first = client.post(
        "/api/tasks",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/tasks",
        json={"title": "Design review", "scheduled_at": "2026-09-03T15:30:00Z"},
    )

    assert second.status_code == 201
