"""The sets of words that count as true or false."""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass


@dataclass(frozen=True)
class BoolRules:
    """Case-insensitive vocabularies for truthy and falsy strings.

    Pass any collection of words; they are normalised (trimmed and lower-cased) on
    construction, so a value only needs to match one once it has been stripped and
    lower-cased too.
    """

    true: Collection[str] = frozenset({"y", "yes", "t", "true", "on", "1"})
    false: Collection[str] = frozenset({"n", "no", "f", "false", "off", "0"})

    def __post_init__(self) -> None:
        true = frozenset(word.strip().lower() for word in self.true)
        false = frozenset(word.strip().lower() for word in self.false)
        clash = true & false
        if clash:
            raise ValueError(f"words marked both true and false: {sorted(clash)}")
        object.__setattr__(self, "true", true)
        object.__setattr__(self, "false", false)


DEFAULT = BoolRules()
