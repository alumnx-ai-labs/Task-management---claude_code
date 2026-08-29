def test_delete_existing_task_returns_204(client):
    created = client.post("/api/tasks", json={"title": "Temp task"}).json()

    response = client.delete(f"/api/tasks/{created['id']}")

    assert response.status_code == 204
    assert client.get("/api/tasks").json()["tasks"] == []


def test_delete_unknown_id_returns_404(client):
    response = client.delete("/api/tasks/does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"


def test_delete_already_deleted_task_returns_404(client):
    created = client.post("/api/tasks", json={"title": "Temp task"}).json()
    client.delete(f"/api/tasks/{created['id']}")

    response = client.delete(f"/api/tasks/{created['id']}")

    assert response.status_code == 404
