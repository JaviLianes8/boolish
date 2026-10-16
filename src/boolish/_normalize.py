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
    Decomposing before lower-casing matters: the Turkish dotted capital I lower-cases to
    ``i`` plus a mark, but decomposes to a plain ``I`` first. Folding is idempotent over
    every code point (a test checks it). Uses the standard library only.
    """
    return str.strip(str.lower(_strip_marks(text)))


def fold_within(text: str, limit: int) -> str | None:
    """Return :func:`fold` of ``text``, or ``None`` once it must exceed ``limit``.

    Folding stops as soon as the result is sure to hold more than ``limit`` non-space
    characters, so hostile input that expands under NFKD costs no more work than the
    longest vocabulary word needs. When it does not stop, the result equals ``fold``.
    """
    parts = []
    seen = 0
    text = str.strip(text)
    for start in range(0, len(text), _CHUNK):
        part = _strip_marks(text[start : start + _CHUNK])
        seen += sum(1 for ch in part if not ch.isspace())
        if seen > limit:
            return None
        parts.append(part)
    return str.strip(str.lower("".join(parts)))
