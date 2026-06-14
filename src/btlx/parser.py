"""Parsing d'un fichier BTLx en modèle de données. / Parse BTLx into the data model.

Tolérant aux espaces de noms (namespaces) : BTLx utilise par défaut
``xmlns="https://www.design2machine.com"``. On supprime le préfixe d'espace de
noms pour rendre la lecture indépendante de la version et du préfixe.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, Optional, Union

from .errors import BtlxParseError
from .model import BtlxFile, FileDescription, Part, Processing, Project, freeze

PathLike = Union[str, Path]

# Sécurité : BTLx n'emploie jamais de DTD. On rejette tout DOCTYPE/ENTITY pour
# bloquer les attaques XXE et « billion laughs » (expansion d'entités).
# Security: BTLx never uses a DTD; reject DOCTYPE/ENTITY to block XXE and
# billion-laughs entity-expansion attacks.
_DTD_PATTERN = re.compile(r"<!\s*(?:DOCTYPE|ENTITY)\b", re.IGNORECASE)

# On privilégie defusedxml si disponible, sinon le parser stdlib protégé par le
# garde-fou ci-dessus. / Prefer defusedxml when installed.
try:  # pragma: no cover - dépend de l'environnement
    from defusedxml.ElementTree import fromstring as _safe_fromstring
except ImportError:  # pragma: no cover
    _safe_fromstring = ET.fromstring


def _local(tag: str) -> str:
    """Retire l'espace de noms d'un tag : '{ns}Part' -> 'Part'."""
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _find(parent: ET.Element, name: str) -> Optional[ET.Element]:
    for child in parent:
        if _local(child.tag) == name:
            return child
    return None


def _iter(parent: ET.Element, name: str) -> Iterable[ET.Element]:
    for child in parent:
        if _local(child.tag) == name:
            yield child


def _text(parent: ET.Element, name: str) -> str:
    el = _find(parent, name)
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def _parse_file_description(root: ET.Element) -> FileDescription:
    el = _find(root, "FileDescription")
    if el is None:
        return FileDescription()
    raw = {_local(c.tag): (c.text or "").strip() for c in el}
    return FileDescription(
        file_name=raw.get("FileName", ""),
        date=raw.get("Date", ""),
        time=raw.get("Time", ""),
        comment=raw.get("Comment", ""),
        raw=freeze(raw),
    )


def _parse_project(root: ET.Element) -> Project:
    el = _find(root, "Project")
    if el is None:
        return Project()
    return Project(name=el.get("Name", ""), comment=_text(el, "Comment"))


def _parse_processings(part_el: ET.Element) -> tuple[Processing, ...]:
    """Lit les usinages, qu'ils soient sous <Processings> ou directs."""
    container = _find(part_el, "Processings")
    source = container if container is not None else part_el
    result = []
    for child in source:
        tag = _local(child.tag)
        # Sous <Part> directement, on ignore les conteneurs structurels connus.
        if container is None and tag in _PART_STRUCTURAL_TAGS:
            continue
        result.append(
            Processing(
                type=tag,
                name=child.get("Name", ""),
                params=freeze(dict(child.attrib)),
            )
        )
    return tuple(result)


_PART_STRUCTURAL_TAGS = {
    "Transformations",
    "GrainDirection",
    "ReferenceSide",
    "Shape",
    "Processings",
}


def _parse_part(part_el: ET.Element) -> Part:
    return Part(
        attrs=freeze(dict(part_el.attrib)),
        processings=_parse_processings(part_el),
    )


def _parse_parts(root: ET.Element) -> tuple[Part, ...]:
    container = _find(root, "Parts")
    source = container if container is not None else root
    return tuple(_parse_part(p) for p in _iter(source, "Part"))


def parse_string(content: str) -> BtlxFile:
    """Parse un BTLx fourni sous forme de chaîne XML.

    :raises BtlxParseError: XML mal formé ou racine ≠ <BTLx>.
    """
    if content is None or not content.strip():
        raise BtlxParseError("Contenu BTLx vide. / Empty BTLx content.")
    if _DTD_PATTERN.search(content):
        raise BtlxParseError(
            "DTD/entité XML refusée pour raisons de sécurité (XXE). "
            "/ XML DTD/entity rejected for security reasons (XXE)."
        )
    try:
        root = _safe_fromstring(content)
    except ET.ParseError as exc:
        raise BtlxParseError(f"XML invalide : {exc}") from exc

    if _local(root.tag) != "BTLx":
        raise BtlxParseError(
            f"Racine inattendue <{_local(root.tag)}>, attendu <BTLx>."
        )

    return BtlxFile(
        version=root.get("Version", ""),
        language=root.get("Language", ""),
        file_description=_parse_file_description(root),
        project=_parse_project(root),
        parts=_parse_parts(root),
    )


def parse_file(path: PathLike, encoding: str = "utf-8") -> BtlxFile:
    """Parse un fichier BTLx depuis le disque.

    :raises BtlxParseError: fichier absent, illisible, ou XML invalide.
    """
    p = Path(path)
    try:
        content = p.read_text(encoding=encoding)
    except FileNotFoundError as exc:
        raise BtlxParseError(f"Fichier introuvable : {p}") from exc
    except OSError as exc:
        raise BtlxParseError(f"Lecture impossible : {p} ({exc})") from exc
    return parse_string(content)
