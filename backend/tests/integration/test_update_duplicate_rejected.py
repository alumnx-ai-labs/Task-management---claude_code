def test_update_that_would_create_a_duplicate_is_rejected(client):
    client.post(
        "/api/tasks",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    )
    other = client.post(
        "/api/tasks",
        json={"title": "Design review", "scheduled_at": "2026-09-04T09:00:00Z"},
    ).json()

    response = client.patch(
        f"/api/tasks/{other['id']}",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_TASK"


def test_update_with_unchanged_title_and_schedule_is_not_a_self_duplicate(client):
    created = client.post(
        "/api/tasks",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    ).json()

    response = client.patch(
        f"/api/tasks/{created['id']}",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z", "description": "Add notes"},
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Add notes"
