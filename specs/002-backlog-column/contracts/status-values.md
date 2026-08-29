# Contract Amendment: `status` enum

Amends `../../001-task-management/contracts/tasks-api.md`. Every endpoint,
request/response shape, status code, and error code documented there is
otherwise unchanged.

## Change

The `status` field on `Task` (and on the `POST /api/tasks` / `PATCH
/api/tasks/{id}` request bodies) accepts one additional value:

| Before | After |
|---|---|
| `"todo"` \| `"in_progress"` \| `"done"` | `"backlog"` \| `"todo"` \| `"in_progress"` \| `"done"` |

- **Backward compatible**: every request/response that was valid before this
  change remains valid — this only widens the accepted set.
- **Default unchanged**: `POST /api/tasks` with no `status` field still
  defaults to `"todo"` (FR-005).
- **No other field, endpoint, or error code is affected.** `DUPLICATE_TASK`
  and `SCHEDULING_CONFLICT` responses behave identically for a task with
  `status: "backlog"` as for any other status (FR-006).

## Example

```json
POST /api/tasks
{
  "title": "Investigate flaky test",
  "status": "backlog"
}
```

```json
201 Created
{
  "id": "…",
  "title": "Investigate flaky test",
  "description": null,
  "scheduled_at": null,
  "status": "backlog",
  "created_at": "…",
  "updated_at": "…"
}
```
