"""Helpers internes de conversion tolérante. / Internal tolerant conversion helpers."""
from __future__ import annotations

from typing import Optional


def to_float(value: Optional[str], default: Optional[float] = None) -> Optional[float]:
    """Convertit en float sans lever d'exception.

    Accepte la virgule décimale ('1,5') utilisée par certains exportateurs.
    Renvoie ``default`` si la valeur est vide/None/illisible.
    """
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        return float(text.replace(",", "."))
    except (ValueError, TypeError):
        return default


def to_int(value: Optional[str], default: Optional[int] = None) -> Optional[int]:
    """Convertit en int sans lever d'exception (gère '3.0' -> 3)."""
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        return int(text)
    except (ValueError, TypeError):
        f = to_float(text)
        if f is None:
            return default
        return int(f)
