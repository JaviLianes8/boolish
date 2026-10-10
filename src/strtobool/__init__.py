"""A typed, dependency-free replacement for the strtobool removed from the stdlib."""

from __future__ import annotations

from strtobool._env import getenv_bool
from strtobool._parse import strtobool
from strtobool._rules import DEFAULT, BoolRules

__all__ = ["DEFAULT", "BoolRules", "getenv_bool", "strtobool"]
__version__ = "0.1.0"
