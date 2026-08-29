# Task Management — Backend

FastAPI + SQLAlchemy (SQLite) REST API. See [../specs/001-task-management/contracts/tasks-api.md](../specs/001-task-management/contracts/tasks-api.md) for the full API contract.

## Setup

```bash
python3 -m venv .venv
./.venv/bin/pip install -e ".[dev]"
```

## Run

```bash
./.venv/bin/uvicorn src.main:app --reload --port 8000
```

The API is served at `http://localhost:8000/api`. CORS is enabled for the Vite dev server (`http://localhost:5173`).

## Test

```bash
./.venv/bin/python -m pytest
```

See [../specs/001-task-management/quickstart.md](../specs/001-task-management/quickstart.md) for the full validation walkthrough.
