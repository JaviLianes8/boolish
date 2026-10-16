"""Text normalisation shared by the parser and the rules."""

from __future__ import annotations

import unicodedata


def normalize(text: str) -> str:
    """Trim surrounding whitespace and lower-case ``text``.

    This is the normalisation applied in strict mode. Case and surrounding space never
    matter; nothing else about the text is changed. The ``str`` methods are called
    directly so a ``str`` subclass cannot override them.
    """
    return str.lower(str.strip(text))


def _strip_marks(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def fold(text: str) -> str:
    """Normalise ``text`` and strip diacritics for lenient matching.

    Compatibility forms are decomposed (full-width letters read as their ASCII forms) and
    combining marks removed, so ``"Sí"`` and ``"OUI"`` fold to ``"si"`` and ``"oui"``.
    Marks are stripped again after lower-casing because lower-casing can add one (the
    Turkish dotted capital I). Uses the standard library only.
    """
    return str.strip(_strip_marks(str.lower(_strip_marks(text))))
