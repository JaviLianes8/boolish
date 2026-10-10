"""Read booleans straight from environment variables."""

from __future__ import annotations

import os
from typing import TypeVar, overload

from strtobool._parse import strtobool
from strtobool._rules import DEFAULT, BoolRules

T = TypeVar("T")


@overload
def getenv_bool(name: str) -> bool | None: ...
@overload
def getenv_bool(name: str, default: T, *, rules: BoolRules = ...) -> bool | T: ...


def getenv_bool(name: str, default: object = None, *, rules: BoolRules = DEFAULT) -> object:
    """Parse the environment variable ``name`` as a bool.

    Returns ``default`` when the variable is unset. When it is set but holds an
    unrecognised value, ``ValueError`` is raised: a misconfigured flag should be loud,
    not silently treated as its default.
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    return strtobool(raw, rules=rules)
