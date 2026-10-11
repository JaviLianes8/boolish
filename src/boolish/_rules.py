"""The sets of words that count as true or false."""

from __future__ import annotations

from collections.abc import Collection, Iterable
from dataclasses import dataclass, field

from boolish._errors import BoolishError
from boolish._normalize import fold, normalize


@dataclass(frozen=True)
class BoolRules:
    """Case-insensitive vocabularies for truthy and falsy strings.

    Pass any collection of words; they are normalised (trimmed and lower-cased) on
    construction, so a value only needs to match one once it has been stripped and
    lower-cased too. In lenient mode the match also ignores accents, so ``"sí"`` in the
    vocabulary matches the input ``"si"`` and the other way round.

    A word that appears in both ``true`` and ``false`` is rejected, as is a pair that
    would collide once accents are folded (that would make lenient matching ambiguous).
    """

    true: Collection[str] = frozenset({"y", "yes", "t", "true", "on", "1"})
    false: Collection[str] = frozenset({"n", "no", "f", "false", "off", "0"})
    true_folded: frozenset[str] = field(default=frozenset(), compare=False, repr=False)
    false_folded: frozenset[str] = field(default=frozenset(), compare=False, repr=False)

    def __post_init__(self) -> None:
        true = frozenset(normalize(word) for word in self.true)
        false = frozenset(normalize(word) for word in self.false)
        clash = true & false
        if clash:
            raise BoolishError(f"words marked both true and false: {sorted(clash)}")
        true_folded = frozenset(fold(word) for word in true)
        false_folded = frozenset(fold(word) for word in false)
        folded_clash = true_folded & false_folded
        if folded_clash:
            raise BoolishError(f"words collide once accents are folded: {sorted(folded_clash)}")
        object.__setattr__(self, "true", true)
        object.__setattr__(self, "false", false)
        object.__setattr__(self, "true_folded", true_folded)
        object.__setattr__(self, "false_folded", false_folded)

    def extend(
        self,
        *,
        true: Iterable[str] = (),
        false: Iterable[str] = (),
    ) -> BoolRules:
        """Return a new ruleset with extra words added to this one.

        The original is left untouched (rulesets are frozen). Use it to layer a few
        custom words on top of :data:`DEFAULT` or :data:`MULTILINGUAL` without rebuilding
        the vocabulary by hand::

            DEFAULT.extend(true={"aye"}, false={"nay"})
        """
        return BoolRules(
            true=frozenset(self.true) | {normalize(word) for word in true},
            false=frozenset(self.false) | {normalize(word) for word in false},
        )


DEFAULT = BoolRules(
    true=frozenset({"y", "yes", "t", "true", "on", "1", "enable", "enabled"}),
    false=frozenset({"n", "no", "f", "false", "off", "0", "disable", "disabled"}),
)

# Vocabularies are stored in their unaccented (ASCII) form on purpose. Strict matching
# needs the accents removed by the writer, while accented input such as "si" written
# "sí" resolves in lenient mode, where accents are folded before the lookup.
MULTILINGUAL = BoolRules(
    true=frozenset(
        {
            "y",
            "yes",
            "t",
            "true",
            "on",
            "1",
            "enable",
            "enabled",
            "active",
            "ok",
            "si",
            "verdadero",  # Spanish
            "oui",
            "vrai",  # French
            "ja",
            "wahr",  # German
            "vero",  # Italian
            "sim",
            "verdadeiro",  # Portuguese
        }
    ),
    false=frozenset(
        {
            "n",
            "no",
            "f",
            "false",
            "off",
            "0",
            "disable",
            "disabled",
            "inactive",
            "falso",  # Spanish and Portuguese
            "non",
            "faux",  # French
            "nein",
            "falsch",  # German
            "nao",  # Portuguese
        }
    ),
)
