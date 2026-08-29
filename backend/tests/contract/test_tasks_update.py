def test_patch_updates_fields_successfully(client):
    created = client.post("/api/tasks", json={"title": "Draft plan"}).json()

    response = client.patch(
        f"/api/tasks/{created['id']}",
        json={"title": "Final plan", "status": "in_progress"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Final plan"
    assert body["status"] == "in_progress"
    assert body["id"] == created["id"]


def test_patch_unknown_id_returns_404(client):
    response = client.patch("/api/tasks/does-not-exist", json={"title": "New"})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"


def test_patch_status_to_and_from_backlog_succeeds(client):
    created = client.post("/api/tasks", json={"title": "Draft plan"}).json()

    to_backlog = client.patch(f"/api/tasks/{created['id']}", json={"status": "backlog"})
    assert to_backlog.status_code == 200
    assert to_backlog.json()["status"] == "backlog"

    back_to_todo = client.patch(f"/api/tasks/{created['id']}", json={"status": "todo"})
    assert back_to_todo.status_code == 200
    assert back_to_todo.json()["status"] == "todo"
