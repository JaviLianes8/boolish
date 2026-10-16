"""Turn a string into a bool."""

from __future__ import annotations

from typing import TypeVar, overload

from boolish._errors import NotBooleanError, kind
from boolish._normalize import fold_within, normalize
from boolish._rules import DEFAULT, BoolRules

T = TypeVar("T")


class _Missing:
    """Sentinel that tells a real default apart from ``None`` as a default."""

    def __repr__(self) -> str:
        return "<no default>"


_MISSING = _Missing()


def match_string(value: str, rules: BoolRules, strict: bool) -> bool | None:
    """Return the boolean meaning of ``value``, or ``None`` if it matches nothing.

    In strict mode (the default) the stripped, lower-cased text must be in the
    vocabulary exactly. In lenient mode accents are folded first, so ``"Sí"`` matches a
    rule written ``"si"`` and the other way round. This never raises; callers decide what
    an unmatched value means.
    """
    token = normalize(value)
    if token in rules.true:
        return True
    if token in rules.false:
        return False
    if not strict:
        folded = fold_within(value, rules._longest)
        if folded in rules._true_folded:
            return True
        if folded in rules._false_folded:
            return False
    return None


@overload
def strtobool(value: str, *, rules: BoolRules = ..., strict: bool = ...) -> bool: ...
@overload
def strtobool(
    value: str, default: T, *, rules: BoolRules = ..., strict: bool = ...
) -> bool | T: ...


def strtobool(
    value: str,
    default: object = _MISSING,
    *,
    rules: BoolRules = DEFAULT,
    strict: bool = True,
) -> object:
    """Return the boolean meaning of ``value``.

    Matching ignores surrounding space and case. With no ``default`` an unrecognised
    value raises :class:`~boolish.NotBooleanError` (a ``ValueError`` subclass); pass a
    ``default`` to get it back instead. The result is a real ``bool`` (the stdlib version
    returned ``1``/``0``). A ``value`` that is not a ``str`` raises ``TypeError``, with
    or without a default: that is a programming error, not unrecognised input.

    Set ``strict=False`` to also fold accents before matching, so ``"Sí"`` resolves
    against a rule spelled ``"si"``. Pass ``rules`` to swap the vocabulary, for example
    :data:`~boolish.MULTILINGUAL`.

    >>> from boolish import strtobool
    >>> strtobool("yes")
    True
    >>> strtobool("Off")
    False
    >>> strtobool("maybe", False)
    False
    """
    if not issubclass(type(value), str):
        raise TypeError(f"strtobool expects a str, not {kind(value)}")
    result = match_string(str.__str__(value), rules, strict)
    if result is not None:
        return result
    if not isinstance(default, _Missing):
        return default
    raise NotBooleanError(value)
