"""Text normalization shared by CER and every DRPF rate."""

from __future__ import annotations

import re
import unicodedata

from opencc import OpenCC

_opencc = OpenCC("s2twp")


def to_traditional(text: str) -> str:
    if not text:
        return text
    return _opencc.convert(text)


def strip_special_markers(text: str) -> str:
    """Remove server-side markers such as ``<{silent}>``."""
    if not text:
        return ""
    return re.sub(r"<\{[^}]*\}>", "", text).strip()


def normalize_for_cer(text: str) -> str:
    """NFKC width folding, OpenCC s2twp, then drop whitespace and punctuation."""
    if not text:
        return ""
    text = strip_special_markers(text)
    text = unicodedata.normalize("NFKC", text)
    text = to_traditional(text)
    return "".join(
        c
        for c in text
        if not c.isspace() and not unicodedata.category(c).startswith("P")
    )
