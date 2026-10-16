"""Typed errors raised by boolish."""

from __future__ import annotations

_PREVIEW = 32


def kind(value: object) -> str:
    """Name the type of ``value`` safely: escaped, and cut to 40 characters."""
    # The base descriptor reads the real name even when a metaclass overrides __name__.
    name = str.__str__(type.__dict__["__name__"].__get__(type(value)))[:40]
    return "".join(ch if ch.isprintable() else ascii(ch)[1:-1] for ch in name)


def preview(value: object) -> str:
    """Describe ``value`` for an error message in a short, bounded form.

    Strings are cut to their first 32 characters, huge integers are named by size, and
    any other type is named rather than printed, so a message never carries a whole
    payload and never runs a foreign ``__repr__``.
    """
    # type() rather than isinstance(): a mock can fake its __class__.
    cls = type(value)
    if value is None or cls is bool:
        return repr(value)
    if issubclass(cls, str):
        text = str.__str__(value)
        return repr(text[:_PREVIEW]) + ("..." if len(text) > _PREVIEW else "")
    if issubclass(cls, int):
        bits = int.bit_length(value)  # type: ignore[arg-type]
        return f"an int of {bits} bits" if bits > 64 else int.__repr__(value)
    if issubclass(cls, float):
        return float.__repr__(value)
    return f"a value of type {kind(value)}"


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
    from when :func:`~boolish.getenv_bool` raised it, and is ``None`` otherwise; then the
    message gives only the length of the value, which may be a secret.

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
        if variable is None:
            message = f"{preview(value)} is not a recognised boolean"
        else:
            # The value of an environment variable may be a secret: give only its size.
            size = len(str.__str__(value)) if issubclass(type(value), str) else 0
            message = (
                f"environment variable {preview(variable)}: a value of {size} characters"
                " is not a recognised boolean"
            )
        super().__init__(message)

    def __reduce__(self) -> tuple[type[NotBooleanError], tuple[object, str | None]]:
        return (type(self), (self.value, self.variable))
