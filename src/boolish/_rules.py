"""The sets of words that count as true or false."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property

from boolish._errors import BoolishError, kind, preview
from boolish._normalize import fold, normalize

_CLASSIC_TRUE = frozenset({"y", "yes", "t", "true", "on", "1"})
_CLASSIC_FALSE = frozenset({"n", "no", "f", "false", "off", "0"})


def _words(words: Iterable[str], side: str) -> frozenset[str]:
    """Normalise a vocabulary, refusing a bare string or a non-string word."""
    if issubclass(type(words), str | bytes | bytearray):
        raise TypeError(f"{side} must be a collection of words, not a single {kind(words)}")
    result = set()
    for word in words:
        if not issubclass(type(word), str):
            raise TypeError(f"{side} words must be str, not {kind(word)}")
        result.add(normalize(str.__str__(word)))
    return frozenset(result)


def _listing(words: frozenset[str]) -> str:
    shown = sorted(words)[:10]
    return ", ".join(preview(word) for word in shown) + (", ..." if len(words) > 10 else "")


@dataclass(frozen=True, init=False)
class BoolRules:
    """Case-insensitive vocabularies for truthy and falsy strings.

    Pass any iterable of words; they are normalised (trimmed and lower-cased) on
    construction and kept as the ``frozenset`` attributes ``true`` and ``false``, so a
    value only needs to match one once it has been stripped and lower-cased too. In
    lenient mode the match also ignores accents, so ``"sí"`` in the vocabulary matches
    the input ``"si"`` and the other way round.

    A word that appears in both ``true`` and ``false`` raises
    :class:`~boolish.BoolishError`, as does a pair that would collide once accents are
    folded (lenient matching would be ambiguous). A bare string instead of a collection,
    or a word that is not a string, raises ``TypeError``. With no arguments the
    vocabulary is :data:`~boolish.CLASSIC`, the removed stdlib function's twelve words.

    >>> from boolish import CLASSIC, BoolRules
    >>> rules = BoolRules(true={"Up"}, false={"down"})
    >>> sorted(rules.true), sorted(rules.false)
    (['up'], ['down'])
    >>> BoolRules() == CLASSIC
    True
    >>> BoolRules(true=["Yes", "on"], false=["off"])
    BoolRules(true=['on', 'yes'], false=['off'])
    """

    __module__ = "boolish"

    true: frozenset[str]
    false: frozenset[str]

    def __init__(
        self,
        true: Iterable[str] = _CLASSIC_TRUE,
        false: Iterable[str] = _CLASSIC_FALSE,
    ) -> None:
        true_words = _words(true, "true")
        false_words = _words(false, "false")
        clash = true_words & false_words
        if clash:
            raise BoolishError(f"words marked both true and false: {_listing(clash)}")
        object.__setattr__(self, "true", true_words)
        object.__setattr__(self, "false", false_words)
        folded_clash = self._true_folded & self._false_folded
        if folded_clash:
            raise BoolishError(f"words collide once accents are folded: {_listing(folded_clash)}")

    # The folded forms are derived data, kept out of the dataclass fields.
    @cached_property
    def _true_folded(self) -> frozenset[str]:
        return frozenset(fold(word) for word in self.true)

    @cached_property
    def _false_folded(self) -> frozenset[str]:
        return frozenset(fold(word) for word in self.false)

    @cached_property
    def _longest(self) -> int:
        """Length of the longest folded word: longer folded input cannot match."""
        return max(map(len, self._true_folded | self._false_folded), default=0)

    def __repr__(self) -> str:
        return f"BoolRules(true={sorted(self.true)!r}, false={sorted(self.false)!r})"

    def extend(
        self,
        *,
        true: Iterable[str] = (),
        false: Iterable[str] = (),
    ) -> BoolRules:
        """Return a new ruleset with extra words added to this one.

        The original is left untouched (rulesets are frozen). Use it to layer a few
        custom words on top of :data:`DEFAULT` or :data:`MULTILINGUAL` without rebuilding
        the vocabulary by hand. The same checks as the constructor apply.

        >>> from boolish import DEFAULT, strtobool
        >>> pirate = DEFAULT.extend(true={"aye"}, false={"nay"})
        >>> strtobool("Aye", rules=pirate), strtobool("yes", rules=pirate)
        (True, True)
        """
        return BoolRules(
            true=self.true | _words(true, "true"),
            false=self.false | _words(false, "false"),
        )


CLASSIC = BoolRules()

DEFAULT = CLASSIC.extend(true={"enable", "enabled"}, false={"disable", "disabled"})

# Vocabularies are stored in their unaccented (ASCII) form on purpose. Strict matching
# needs the accents removed by the writer, while accented input such as "si" written
# "sí" resolves in lenient mode, where accents are folded before the lookup.
MULTILINGUAL = DEFAULT.extend(
    true={
        "active",
        "ok",
        "si",  # Spanish and Italian
        "verdadero",  # Spanish
        "oui",
        "vrai",  # French
        "ja",
        "wahr",  # German
        "vero",  # Italian
        "sim",
        "verdadeiro",  # Portuguese
    },
    false={
        "inactive",
        "falso",  # Spanish, Italian and Portuguese
        "non",
        "faux",  # French
        "nein",
        "falsch",  # German
        "nao",  # Portuguese
    },
)
