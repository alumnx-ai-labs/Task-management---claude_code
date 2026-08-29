def test_drag_onto_occupied_slot_is_rejected_and_original_untouched(client):
    occupied_at = "2026-09-06T11:00:00Z"
    client.post("/api/tasks", json={"title": "Busy task", "scheduled_at": occupied_at})
    dragged = client.post(
        "/api/tasks", json={"title": "Dragged task", "scheduled_at": "2026-09-07T09:00:00Z"}
    ).json()

    response = client.patch(
        f"/api/tasks/{dragged['id']}", json={"scheduled_at": occupied_at}
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "SCHEDULING_CONFLICT"

    unchanged = client.get("/api/tasks").json()["tasks"]
    still_dragged = next(t for t in unchanged if t["id"] == dragged["id"])
    assert still_dragged["scheduled_at"].startswith("2026-09-07T09:00:00")
