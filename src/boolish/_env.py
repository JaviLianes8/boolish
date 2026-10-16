"""Read booleans straight from environment variables."""

from __future__ import annotations

import os
from typing import TypeVar, overload

from boolish._errors import NotBooleanError
from boolish._parse import strtobool
from boolish._rules import DEFAULT, BoolRules

T = TypeVar("T")


@overload
def getenv_bool(name: str, *, rules: BoolRules = ..., strict: bool = ...) -> bool | None: ...
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

    Returns ``default`` (``None`` unless given) when the variable is unset. When it is
    set, even to an empty string, but holds an unrecognised value,
    :class:`~boolish.NotBooleanError` is raised with ``variable`` set to ``name``: a
    misconfigured flag should be loud, not silently treated as its default.

    Pass ``strict=False`` to fold accents, or ``rules`` to swap the vocabulary.

    >>> import os
    >>> from boolish import NotBooleanError, getenv_bool
    >>> os.environ["FEATURE_X"] = "true"
    >>> getenv_bool("FEATURE_X")
    True
    >>> getenv_bool("FEATURE_UNSET_EXAMPLE", False)
    False
    >>> os.environ["FEATURE_X"] = "banana"
    >>> try:
    ...     getenv_bool("FEATURE_X", False)
    ... except NotBooleanError as error:
    ...     print(error)
    environment variable 'FEATURE_X': 'banana' is not a recognised boolean
    >>> del os.environ["FEATURE_X"]
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return strtobool(raw, rules=rules, strict=strict)
    except NotBooleanError:
        raise NotBooleanError(raw, variable=name) from None
