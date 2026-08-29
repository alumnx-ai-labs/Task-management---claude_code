def test_updating_task_with_its_own_schedule_succeeds(client):
    created = client.post(
        "/api/tasks",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    ).json()

    response = client.patch(
        f"/api/tasks/{created['id']}",
        json={"scheduled_at": "2026-09-03T14:30:00Z", "status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_updating_task_with_its_own_title_and_schedule_is_not_a_self_duplicate(client):
    created = client.post(
        "/api/tasks",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    ).json()

    response = client.patch(
        f"/api/tasks/{created['id']}",
        json={"title": "Team Sync", "scheduled_at": "2026-09-03T14:30:00Z"},
    )

    assert response.status_code == 200
