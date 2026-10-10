"""A typed, dependency-free replacement for the strtobool removed from the stdlib."""

from __future__ import annotations

from boolish._env import getenv_bool
from boolish._parse import strtobool
from boolish._rules import DEFAULT, BoolRules

__all__ = ["DEFAULT", "BoolRules", "getenv_bool", "strtobool"]
__version__ = "0.1.0"
