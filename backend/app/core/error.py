# app/core/errors.py
import logging
import traceback
from fastapi import HTTPException
from app.core.config import settings

log = logging.getLogger("app.errors")

def _format_tb(exc: Exception) -> str:
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))


class LoggedHTTPException(HTTPException):
    """
    Drop-in replacement for HTTPException that logs traceback when you pass `exc=...`.
    """
    def __init__(self, status_code: int, detail=None, *, exc: Exception | None = None):
        if exc is not None:
            tb = _format_tb(exc)
            log.error("HTTP %s: %s\n%s", status_code, detail or "", tb)
            if not settings.is_production and isinstance(detail, dict):
                detail = {**detail, "traceback": tb}
        super().__init__(status_code=status_code, detail=detail)
