"""Agrégats métier : liste de débit, volumes, récap matériaux.

Business aggregates: cut list, volumes, material summary.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .model import BtlxFile, Part


@dataclass(frozen=True)
class CutListRow:
    """Ligne de liste de débit (pièces identiques regroupées)."""

    designation: str
    material: str
    length: float  # mm
    width: float  # mm
    height: float  # mm
    count: int
    total_length: float  # mm (length × count)
    total_volume_m3: float


def _key(part: Part) -> Tuple[str, str, float, float, float]:
    return (
        part.designation,
        part.material,
        round(part.length, 1),
        round(part.width, 1),
        round(part.height, 1),
    )


def cut_list(file: BtlxFile) -> List[CutListRow]:
    """Regroupe les pièces identiques en une liste de débit triée.

    Le regroupement se fait sur désignation + matériau + dimensions. L'ordre de
    première apparition est conservé pour rester déterministe.
    """
    buckets: "OrderedDict[Tuple, List[Part]]" = OrderedDict()
    for part in file.parts:
        buckets.setdefault(_key(part), []).append(part)

    rows: List[CutListRow] = []
    for parts in buckets.values():
        ref = parts[0]
        count = sum(p.count for p in parts)
        rows.append(
            CutListRow(
                designation=ref.designation,
                material=ref.material,
                length=ref.length,
                width=ref.width,
                height=ref.height,
                count=count,
                total_length=ref.length * count,
                total_volume_m3=ref.volume_m3 * count,
            )
        )
    return rows


def total_volume_m3(file: BtlxFile) -> float:
    """Volume total de bois en m³ (toutes pièces × quantités)."""
    return sum(p.volume_m3 * p.count for p in file.parts)


def total_length_m(file: BtlxFile) -> float:
    """Longueur linéaire totale en mètres."""
    return sum(p.length * p.count for p in file.parts) / 1000.0


def total_weight_kg(file: BtlxFile) -> Optional[float]:
    """Poids total en kg si tous les poids sont renseignés, sinon None."""
    weights = [p.weight for p in file.parts]
    if any(w is None for w in weights):
        return None
    return sum((w or 0.0) * p.count for w, p in zip(weights, file.parts))


def material_summary(file: BtlxFile) -> "OrderedDict[str, dict]":
    """Récapitulatif par matériau : nb de pièces, volume, longueur."""
    summary: "OrderedDict[str, dict]" = OrderedDict()
    for part in file.parts:
        mat = part.material or "—"
        entry = summary.setdefault(
            mat, {"count": 0, "volume_m3": 0.0, "length_m": 0.0}
        )
        entry["count"] += part.count
        entry["volume_m3"] += part.volume_m3 * part.count
        entry["length_m"] += part.length * part.count / 1000.0
    return summary


def processing_summary(file: BtlxFile) -> "OrderedDict[str, int]":
    """Compte les usinages par type sur l'ensemble du fichier."""
    counts: "OrderedDict[str, int]" = OrderedDict()
    for part in file.parts:
        for proc in part.processings:
            counts[proc.type] = counts.get(proc.type, 0) + 1
    return counts


def summary(file: BtlxFile) -> dict:
    """Synthèse globale prête à sérialiser (JSON)."""
    return {
        "version": file.version,
        "project": file.project.name,
        "distinct_parts": len(file.parts),
        "total_parts": file.part_count,
        "total_length_m": round(total_length_m(file), 3),
        "total_volume_m3": round(total_volume_m3(file), 4),
        "total_weight_kg": (
            round(total_weight_kg(file), 2)
            if total_weight_kg(file) is not None
            else None
        ),
        "materials": {
            mat: {
                "count": v["count"],
                "volume_m3": round(v["volume_m3"], 4),
                "length_m": round(v["length_m"], 3),
            }
            for mat, v in material_summary(file).items()
        },
        "processings": dict(processing_summary(file)),
    }
