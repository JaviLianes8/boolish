"""Typed errors raised by boolish."""

from __future__ import annotations

_PREVIEW = 32


def preview(value: object) -> str:
    """Describe ``value`` for an error message in a short, bounded form.

    Strings are cut to their first 32 characters, huge integers are named by size, and
    any other type is named rather than printed, so a message never carries a whole
    payload and never runs a foreign ``__repr__``.
    """
    if value is None or isinstance(value, bool):
        return repr(value)
    if isinstance(value, str):
        head = str.__getitem__(value, slice(None, _PREVIEW))
        return str.__repr__(head) + ("..." if len(value) > _PREVIEW else "")
    if isinstance(value, int):
        if value.bit_length() > 64:
            return f"an int of {value.bit_length()} bits"
        return int.__repr__(value)
    if isinstance(value, float):
        return float.__repr__(value)
    return f"a value of type {type(value).__name__[:40]}"


class BoolishError(ValueError):
    """Base class for every error boolish raises.

    It subclasses :class:`ValueError`, so code that already catches ``ValueError``
    keeps working while new code can catch :class:`BoolishError` for exactly this
    library's failures. Building a :class:`~boolish.BoolRules` with a word on both sides
    raises it directly:

    >>> from boolish import BoolRules
    >>> BoolRules(true={"on"}, false={"on"})
    Traceback (most recent call last):
    ...
    boolish.BoolishError: words marked both true and false: 'on'
    """

    __module__ = "boolish"


class NotBooleanError(BoolishError):
    """Raised when a value cannot be understood as a boolean.

    The offending value is kept, whole, on the ``value`` attribute; the message shows at
    most its first 32 characters. ``variable`` names the environment variable it came
    from when :func:`~boolish.getenv_bool` raised it, and is ``None`` otherwise.

    >>> from boolish import NotBooleanError, strtobool
    >>> try:
    ...     strtobool("banana")
    ... except NotBooleanError as error:
    ...     print(error.value, error.variable)
    banana None
    """

    __module__ = "boolish"

    def __init__(self, value: object, variable: str | None = None) -> None:
        self.value = value
        self.variable = variable
        message = f"{preview(value)} is not a recognised boolean"
        if variable is not None:
            message = f"environment variable {preview(variable)}: {message}"
        super().__init__(message)

    def __reduce__(self) -> tuple[type[NotBooleanError], tuple[object, str | None]]:
        return (type(self), (self.value, self.variable))
