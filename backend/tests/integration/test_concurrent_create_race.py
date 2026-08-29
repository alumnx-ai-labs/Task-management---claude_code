import threading


def test_concurrent_conflicting_creates_exactly_one_succeeds(client):
    barrier = threading.Barrier(2)
    results = [None, None]

    def make_request(index, payload):
        barrier.wait()
        results[index] = client.post("/api/tasks", json=payload)

    payload_a = {"title": "Race A", "scheduled_at": "2026-09-05T10:00:00Z"}
    payload_b = {"title": "Race B", "scheduled_at": "2026-09-05T10:00:00Z"}

    thread_a = threading.Thread(target=make_request, args=(0, payload_a))
    thread_b = threading.Thread(target=make_request, args=(1, payload_b))
    thread_a.start()
    thread_b.start()
    thread_a.join()
    thread_b.join()

    statuses = sorted(r.status_code for r in results)
    assert statuses == [201, 409]

    remaining = client.get("/api/tasks").json()["tasks"]
    scheduled_at_10am = [t for t in remaining if t["scheduled_at"] and "10:00:00" in t["scheduled_at"]]
    assert len(scheduled_at_10am) == 1
