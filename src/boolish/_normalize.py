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


_CHUNK = 1024


def _strip_marks(text: str) -> str:
    """Decompose ``text`` (NFKD) and drop every combining character.

    CPython's ``normalize`` slows down more than linearly on long runs of marks, so the
    text goes through in chunks. That gives the same result as one call: decomposition
    is per character, and the reordering NFKD adds only moves combining characters,
    which are all dropped here.
    """
    if text.isascii():
        return text
    parts = []
    for start in range(0, len(text), _CHUNK):
        decomposed = unicodedata.normalize("NFKD", text[start : start + _CHUNK])
        parts.append("".join(ch for ch in decomposed if not unicodedata.combining(ch)))
    return "".join(parts)


def fold(text: str) -> str:
    """Normalise ``text`` and strip diacritics for lenient matching.

    Compatibility forms are decomposed (full-width letters read as their ASCII forms) and
    combining marks removed, so ``"Sí"`` and ``"OUI"`` fold to ``"si"`` and ``"oui"``.
    Marks are stripped again after lower-casing because lower-casing can add one (the
    Turkish dotted capital I). Uses the standard library only.
    """
    return str.strip(_strip_marks(str.lower(_strip_marks(text))))
