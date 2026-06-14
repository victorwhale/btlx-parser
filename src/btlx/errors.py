"""Exceptions du parser BTLx. / BTLx parser exceptions."""
from __future__ import annotations


class BtlxError(Exception):
    """Erreur de base pour toute opération BTLx."""


class BtlxParseError(BtlxError):
    """Le contenu n'est pas un BTLx XML valide.

    Levée pour un XML mal formé ou un élément racine inattendu.
    """
