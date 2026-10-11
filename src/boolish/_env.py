"""Read booleans straight from environment variables."""

from __future__ import annotations

import os
from typing import TypeVar, overload

from boolish._parse import strtobool
from boolish._rules import DEFAULT, BoolRules

T = TypeVar("T")


@overload
def getenv_bool(name: str) -> bool | None: ...
@overload
def getenv_bool(
    name: str, default: T, *, rules: BoolRules = ..., strict: bool = ...
) -> bool | T: ...


def getenv_bool(
    name: str,
    default: object = None,
    *,
    rules: BoolRules = DEFAULT,
    strict: bool = True,
) -> object:
    """Parse the environment variable ``name`` as a bool.

    Returns ``default`` when the variable is unset. When it is set but holds an
    unrecognised value, :class:`~boolish.NotBooleanError` is raised: a misconfigured flag
    should be loud, not silently treated as its default.

    Pass ``strict=False`` to fold accents, or ``rules`` to swap the vocabulary.

    >>> import os
    >>> os.environ["FEATURE_X"] = "true"
    >>> getenv_bool("FEATURE_X")
    True
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    return strtobool(raw, rules=rules, strict=strict)
