"""Text normalisation shared by the parser and the rules."""

from __future__ import annotations

import unicodedata


def normalize(text: str) -> str:
    """Trim surrounding whitespace and lower-case ``text``.

    This is the normalisation applied in strict mode. Case and surrounding space never
    matter; nothing else about the text is changed.
    """
    return text.strip().lower()


def fold(text: str) -> str:
    """Normalise ``text`` and strip diacritics for lenient matching.

    On top of :func:`normalize`, combining marks are removed so that accented input
    matches its unaccented spelling: ``"Sí"`` and ``"OUI"`` fold to ``"si"`` and
    ``"oui"``. Decomposition uses the standard library only.
    """
    decomposed = unicodedata.normalize("NFKD", normalize(text))
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))
