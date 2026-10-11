"""Typed errors raised by boolish."""

from __future__ import annotations


class BoolishError(ValueError):
    """Base class for every error boolish raises.

    It subclasses :class:`ValueError`, so code that already catches ``ValueError``
    keeps working while new code can catch :class:`BoolishError` for exactly this
    library's failures.
    """


class NotBooleanError(BoolishError):
    """Raised when a value cannot be understood as a boolean.

    The offending value is kept on the ``value`` attribute for inspection.
    """

    def __init__(self, value: object) -> None:
        self.value = value
        super().__init__(f"{value!r} is not a recognised boolean")
