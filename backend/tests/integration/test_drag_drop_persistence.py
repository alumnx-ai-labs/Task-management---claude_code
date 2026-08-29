def test_drag_to_new_status_and_free_time_persists(client):
    created = client.post("/api/tasks", json={"title": "Draft report"}).json()

    response = client.patch(
        f"/api/tasks/{created['id']}",
        json={"status": "in_progress", "scheduled_at": "2026-09-06T11:00:00Z"},
    )
    assert response.status_code == 200

    tasks = client.get("/api/tasks").json()["tasks"]
    updated = next(t for t in tasks if t["id"] == created["id"])
    assert updated["status"] == "in_progress"
    assert updated["scheduled_at"].startswith("2026-09-06T11:00:00")


def test_drag_to_new_status_only_leaves_schedule_untouched(client):
    created = client.post(
        "/api/tasks",
        json={"title": "Draft report", "scheduled_at": "2026-09-06T11:00:00Z"},
    ).json()

    response = client.patch(f"/api/tasks/{created['id']}", json={"status": "done"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "done"
    assert body["scheduled_at"].startswith("2026-09-06T11:00:00")
