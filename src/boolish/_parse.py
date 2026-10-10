"""Turn a string into a bool."""

from __future__ import annotations

from typing import TypeVar, overload

from boolish._rules import DEFAULT, BoolRules

T = TypeVar("T")


class _Missing:
    """Sentinel that tells a real default apart from ``None`` as a default."""


_MISSING = _Missing()


@overload
def strtobool(value: str, *, rules: BoolRules = ...) -> bool: ...
@overload
def strtobool(value: str, default: T, *, rules: BoolRules = ...) -> bool | T: ...


def strtobool(value: str, default: object = _MISSING, *, rules: BoolRules = DEFAULT) -> object:
    """Return the boolean meaning of ``value``.

    Matching ignores surrounding space and case. With no ``default`` an unrecognised
    value raises ``ValueError``; pass a ``default`` to get it back instead. The result
    is a real ``bool`` (the stdlib version returned ``1``/``0``).
    """
    token = value.strip().lower()
    if token in rules.true:
        return True
    if token in rules.false:
        return False
    if not isinstance(default, _Missing):
        return default
    raise ValueError(f"{value!r} is not a recognised boolean")
