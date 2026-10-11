"""A typed, dependency-free replacement for the strtobool removed from the stdlib.

Parse and coerce boolean-ish values into real ``bool`` results. The entry points are
:func:`strtobool` (string in, matching the stdlib), :func:`to_bool` (any boolean-ish
value), the non-raising predicates :func:`is_truthy` and :func:`is_falsy`, and
:func:`getenv_bool` for environment variables. Vocabularies are :class:`BoolRules`
instances; :data:`DEFAULT` and :data:`MULTILINGUAL` are ready to use.
"""

from __future__ import annotations

from boolish._coerce import BoolLike, is_falsy, is_truthy, to_bool
from boolish._env import getenv_bool
from boolish._errors import BoolishError, NotBooleanError
from boolish._parse import strtobool
from boolish._rules import DEFAULT, MULTILINGUAL, BoolRules
from boolish._version import __version__ as __version__

__all__ = [
    "DEFAULT",
    "MULTILINGUAL",
    "BoolLike",
    "BoolRules",
    "BoolishError",
    "NotBooleanError",
    "getenv_bool",
    "is_falsy",
    "is_truthy",
    "strtobool",
    "to_bool",
]
