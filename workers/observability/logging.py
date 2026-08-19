"""Structured logging for the worker.

Re-exports the API's JSON logging setup rather than duplicating it —
the worker currently runs in the same Python environment as apps/api
(see docs/16_MEMORY.md). If the worker ever gets its own environment,
this becomes a real independent implementation instead of a re-export.
"""

from app.core.logging import configure_logging

__all__ = ["configure_logging"]
