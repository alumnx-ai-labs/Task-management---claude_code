def test_list_tasks_empty(client):
    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.json() == {"tasks": []}


def test_list_tasks_populated_shape(client):
    client.post("/api/tasks", json={"title": "Task A"})
    client.post("/api/tasks", json={"title": "Task B"})

    response = client.get("/api/tasks")

    assert response.status_code == 200
    body = response.json()
    assert len(body["tasks"]) == 2
    titles = {t["title"] for t in body["tasks"]}
    assert titles == {"Task A", "Task B"}
