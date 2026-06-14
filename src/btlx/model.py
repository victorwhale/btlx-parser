"""Modèle de données immuable BTLx. / Immutable BTLx data model.

Toutes les longueurs BTLx sont en millimètres (mm), conformément au standard
BTLx (design2machine.com). Les volumes calculés sont en m³, les poids en kg.

All BTLx lengths are millimetres (mm) per the BTLx standard; computed volumes
are m³ and weights kg.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Optional, Tuple

from ._utils import to_float, to_int

_EMPTY: Mapping[str, str] = MappingProxyType({})


def freeze(attrs: Optional[Mapping[str, str]]) -> Mapping[str, str]:
    """Renvoie une vue en lecture seule des attributs (immutabilité)."""
    if not attrs:
        return _EMPTY
    return MappingProxyType(dict(attrs))


@dataclass(frozen=True)
class FileDescription:
    """Métadonnées du fichier (<FileDescription>)."""

    file_name: str = ""
    date: str = ""
    time: str = ""
    comment: str = ""
    raw: Mapping[str, str] = field(default_factory=lambda: _EMPTY)


@dataclass(frozen=True)
class Project:
    """Projet / chantier (<Project>)."""

    name: str = ""
    comment: str = ""


# Classement des usinages BTLx par grande famille, pour filtrer facilement.
# Classify BTLx processings into coarse families for easy filtering.
PROCESSING_CATEGORIES: Mapping[str, str] = MappingProxyType(
    {
        # coupes / cuts
        "JackRafterCut": "cut",
        "Cut": "cut",
        "DoubleCut": "cut",
        "EndCut": "cut",
        "ChamferCut": "cut",
        "ShoulderCut": "cut",
        "LongitudinalCut": "cut",
        # perçages / drillings
        "Drilling": "drilling",
        "Hole": "drilling",
        # assemblages / joints
        "Mortise": "joint",
        "Tenon": "joint",
        "Lap": "joint",
        "Slot": "joint",
        "Step": "joint",
        "House": "joint",
        "Cross": "joint",
        "DovetailMortise": "joint",
        "DovetailTenon": "joint",
        "BridleJoint": "joint",
        "ScarfJoint": "joint",
        # poches / contours
        "Pocket": "pocket",
        "Profile": "pocket",
        "FreeContour": "pocket",
        # marquage / texte
        "Marking": "marking",
        "Text": "marking",
    }
)


@dataclass(frozen=True)
class Processing:
    """Un usinage appliqué à une pièce (coupe, perçage, tenon, mortaise...).

    BTLx définit ~40 types d'usinage. Plutôt que de typer chacun, on conserve
    le nom de balise dans ``type`` et tous les attributs dans ``params`` — ce
    qui rend le parser robuste face à n'importe quel fichier réel.
    """

    type: str
    name: str = ""
    params: Mapping[str, str] = field(default_factory=lambda: _EMPTY)

    @property
    def category(self) -> str:
        """Famille de l'usinage : cut, drilling, joint, pocket, marking, other."""
        return PROCESSING_CATEGORIES.get(self.type, "other")

    def param_float(self, key: str, default: Optional[float] = None) -> Optional[float]:
        return to_float(self.params.get(key), default)

    def param_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        return to_int(self.params.get(key), default)


@dataclass(frozen=True)
class Position:
    """Point de référence de la pièce dans le bâtiment (mm).

    Issu de <Transformations><Transformation><Position><ReferencePoint>.
    Utile pour le placement à l'assemblage.
    """

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Part:
    """Une pièce de bois (<Part>) avec ses usinages.

    Les attributs bruts restent accessibles via ``attrs`` ; les propriétés
    typées couvrent les champs les plus utiles d'une liste de débit.
    """

    attrs: Mapping[str, str] = field(default_factory=lambda: _EMPTY)
    processings: Tuple[Processing, ...] = ()
    position: Optional[Position] = None

    # --- Identité ---------------------------------------------------------
    @property
    def number(self) -> str:
        return self.attrs.get("SingleMemberNumber", "")

    @property
    def designation(self) -> str:
        return self.attrs.get("Designation", "")

    @property
    def assembly(self) -> str:
        return self.attrs.get("AssemblyNumber", "")

    @property
    def annotation(self) -> str:
        return self.attrs.get("Annotation", "")

    # --- Matériau ---------------------------------------------------------
    @property
    def material(self) -> str:
        return self.attrs.get("Material") or self.attrs.get("Timber", "")

    @property
    def timber_grade(self) -> str:
        return self.attrs.get("TimberGrade", "")

    # --- Quantité & dimensions (mm) --------------------------------------
    @property
    def count(self) -> int:
        return to_int(self.attrs.get("Count"), 1) or 1

    @property
    def length(self) -> float:
        return to_float(self.attrs.get("Length"), 0.0) or 0.0

    @property
    def width(self) -> float:
        return to_float(self.attrs.get("Width"), 0.0) or 0.0

    @property
    def height(self) -> float:
        return to_float(self.attrs.get("Height"), 0.0) or 0.0

    @property
    def weight(self) -> Optional[float]:
        """Poids unitaire en kg si présent dans le fichier, sinon None."""
        return to_float(self.attrs.get("Weight"))

    # --- Dérivés ----------------------------------------------------------
    @property
    def volume_m3(self) -> float:
        """Volume d'une seule pièce en m³ (L×l×h, mm³ → m³)."""
        return self.length * self.width * self.height / 1_000_000_000.0

    @property
    def cross_section(self) -> str:
        """Section transversale normalisée, ex. '80x160'."""
        return f"{round(self.width)}x{round(self.height)}"

    def processings_of(self, category: str) -> Tuple[Processing, ...]:
        """Usinages d'une catégorie donnée (cut, drilling, joint, ...)."""
        return tuple(p for p in self.processings if p.category == category)

    @property
    def has_joinery(self) -> bool:
        """Vrai si la pièce comporte au moins un assemblage."""
        return any(p.category == "joint" for p in self.processings)


@dataclass(frozen=True)
class BtlxFile:
    """Document BTLx complet et parsé."""

    version: str = ""
    language: str = ""
    file_description: FileDescription = field(default_factory=FileDescription)
    project: Project = field(default_factory=Project)
    parts: Tuple[Part, ...] = ()

    @property
    def part_count(self) -> int:
        """Nombre total de pièces (somme des Count)."""
        return sum(p.count for p in self.parts)
