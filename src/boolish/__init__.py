"""A typed, dependency-free replacement for the strtobool removed from the stdlib.

Parse and coerce boolean-ish values into real ``bool`` results. The entry points are
:func:`strtobool` (string in, as in the stdlib), :func:`to_bool` (any :data:`BoolLike`
value), the non-raising predicates :func:`is_truthy` and :func:`is_falsy`, and
:func:`getenv_bool` for environment variables. Vocabularies are :class:`BoolRules`
instances; three are ready to use:

- :data:`CLASSIC`: the twelve words of the removed ``distutils.util.strtobool``.
- :data:`DEFAULT`: ``CLASSIC`` plus ``enable``/``enabled`` and ``disable``/``disabled``.
- :data:`MULTILINGUAL`: ``DEFAULT`` plus yes/no and true/false words in Spanish,
  French, German, Italian and Portuguese, and ``active``/``ok``/``inactive``.

>>> from boolish import CLASSIC, DEFAULT, MULTILINGUAL, strtobool, to_bool
>>> sorted(CLASSIC.true)
['1', 'on', 't', 'true', 'y', 'yes']
>>> sorted(DEFAULT.false - CLASSIC.false)
['disable', 'disabled']
>>> strtobool("Nein", rules=MULTILINGUAL)
False
>>> strtobool("enabled", "unknown", rules=CLASSIC)
'unknown'

:data:`BoolLike` is the type of what :func:`to_bool` accepts:
``bool | int | float | str | None``.

>>> from boolish import BoolLike
>>> value: BoolLike = 0.0
>>> to_bool(value)
False
"""

from boolish._coerce import BoolLike, is_falsy, is_truthy, to_bool
from boolish._env import getenv_bool
from boolish._errors import BoolishError, NotBooleanError
from boolish._parse import strtobool
from boolish._rules import CLASSIC, DEFAULT, MULTILINGUAL, BoolRules
from boolish._version import __version__ as __version__

__all__ = [
    "CLASSIC",
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
