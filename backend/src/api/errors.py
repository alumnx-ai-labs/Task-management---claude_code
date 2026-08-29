from typing import Any, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """Base for every business-rule error, mapped to the shared error envelope."""

    status_code: int = 400
    code: str = "ERROR"

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DuplicateTaskError(ApiError):
    status_code = 409
    code = "DUPLICATE_TASK"


class SchedulingConflictError(ApiError):
    status_code = 409
    code = "SCHEDULING_CONFLICT"


class TaskNotFoundError(ApiError):
    status_code = 404
    code = "TASK_NOT_FOUND"


def _envelope(code: str, message: str, details: Optional[dict[str, Any]] = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or {}}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Pydantic v2 embeds the raw originating exception in each error's `ctx`
        # (and sometimes the raw request value in `input`), neither of which is
        # guaranteed JSON-serializable — so only pass through the safe fields.
        safe_errors = [
            {
                "loc": [str(part) for part in err.get("loc", [])],
                "msg": err.get("msg"),
                "type": err.get("type"),
            }
            for err in exc.errors()
        ]
        first = safe_errors[0] if safe_errors else {}
        field = ".".join(part for part in first.get("loc", []) if part != "body")
        message = first.get("msg") or "Invalid request"
        if field:
            message = f"{field}: {message}"
        return JSONResponse(
            status_code=422,
            content=_envelope("VALIDATION_ERROR", message, {"errors": safe_errors}),
        )
