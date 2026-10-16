"""Coerce any boolean-ish value, not only strings, into a real bool."""

from __future__ import annotations

import math
from typing import TypeVar, overload

from boolish._errors import NotBooleanError
from boolish._parse import _MISSING, _Missing, match_string
from boolish._rules import DEFAULT, BoolRules

T = TypeVar("T")

BoolLike = bool | int | float | str | None


def _coerce_number(value: int | float, strict: bool) -> bool | None:
    """Map a number to a bool, or ``None`` when it is not boolean-ish."""
    # The base-class methods read the plain value, so a subclass cannot lie about it.
    number = float.__float__(value) if isinstance(value, float) else int.__int__(value)
    if isinstance(number, float) and not math.isfinite(number):
        return None
    if number == 0:
        return False
    if number == 1:
        return True
    if not strict:
        return True
    return None


def _resolve(value: object, rules: BoolRules, strict: bool) -> bool | None:
    """Return the bool meaning of any value, or ``None`` if it has none."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return _coerce_number(value, strict)
    if isinstance(value, str):
        return match_string(value, rules, strict)
    return None


@overload
def to_bool(value: BoolLike, *, rules: BoolRules = ..., strict: bool = ...) -> bool: ...
@overload
def to_bool(
    value: BoolLike, default: T, *, rules: BoolRules = ..., strict: bool = ...
) -> bool | T: ...


def to_bool(
    value: BoolLike,
    default: object = _MISSING,
    *,
    rules: BoolRules = DEFAULT,
    strict: bool = True,
) -> object:
    """Coerce ``value`` to a bool, accepting more than a string.

    Booleans pass through unchanged. The numbers ``0`` and ``1`` (``int`` or ``float``)
    map to ``False`` and ``True``. Strings go through the vocabulary exactly as
    :func:`~boolish.strtobool` does. ``None``, anything unrecognised, and any other type
    either return ``default`` (when one is given) or raise
    :class:`~boolish.NotBooleanError`.

    In lenient mode (``strict=False``) accents are folded for strings and any non-zero,
    finite number counts as ``True``.

    >>> to_bool(1)
    True
    >>> to_bool("off")
    False
    >>> to_bool(None, False)
    False
    """
    result = _resolve(value, rules, strict)
    if result is not None:
        return result
    if not isinstance(default, _Missing):
        return default
    raise NotBooleanError(value)


def is_truthy(value: BoolLike, *, rules: BoolRules = DEFAULT, strict: bool = True) -> bool:
    """Return ``True`` only when ``value`` is recognised as truthy, never raising.

    Anything unknown, including ``None`` and unmatched strings, is ``False``. Handy in an
    ``if`` where an unparseable value should simply count as "no".

    >>> is_truthy("yes")
    True
    >>> is_truthy("maybe")
    False
    """
    return _resolve(value, rules, strict) is True


def is_falsy(value: BoolLike, *, rules: BoolRules = DEFAULT, strict: bool = True) -> bool:
    """Return ``True`` only when ``value`` is recognised as falsy, never raising.

    Anything unknown, including ``None`` and unmatched strings, is ``False``. It is the
    mirror of :func:`is_truthy`, not its negation.

    >>> is_falsy("off")
    True
    >>> is_falsy("maybe")
    False
    """
    return _resolve(value, rules, strict) is False
