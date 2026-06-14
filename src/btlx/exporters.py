"""Exports : dict / JSON / CSV. / Exports: dict / JSON / CSV."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from .aggregate import CutListRow, cut_list, summary
from .model import BtlxFile, Part


def part_to_dict(part: Part) -> dict:
    """Sérialise une pièce avec ses champs typés + attributs bruts."""
    return {
        "number": part.number,
        "designation": part.designation,
        "assembly": part.assembly,
        "material": part.material,
        "timber_grade": part.timber_grade,
        "count": part.count,
        "length": part.length,
        "width": part.width,
        "height": part.height,
        "cross_section": part.cross_section,
        "weight": part.weight,
        "volume_m3": round(part.volume_m3, 6),
        "has_joinery": part.has_joinery,
        "position": (
            {"x": part.position.x, "y": part.position.y, "z": part.position.z}
            if part.position is not None
            else None
        ),
        "processings": [
            {
                "type": p.type,
                "name": p.name,
                "category": p.category,
                "params": dict(p.params),
            }
            for p in part.processings
        ],
        "attrs": dict(part.attrs),
    }


def file_to_dict(file: BtlxFile) -> dict:
    """Sérialise le document BTLx complet."""
    return {
        "version": file.version,
        "language": file.language,
        "file_description": {
            "file_name": file.file_description.file_name,
            "date": file.file_description.date,
            "time": file.file_description.time,
            "comment": file.file_description.comment,
        },
        "project": {
            "name": file.project.name,
            "comment": file.project.comment,
        },
        "parts": [part_to_dict(p) for p in file.parts],
        "summary": summary(file),
    }


def to_json(file: BtlxFile, indent: int = 2) -> str:
    """Renvoie le document BTLx complet en JSON."""
    return json.dumps(file_to_dict(file), indent=indent, ensure_ascii=False)


_CUTLIST_HEADER = [
    "designation",
    "material",
    "length_mm",
    "width_mm",
    "height_mm",
    "count",
    "total_length_mm",
    "total_volume_m3",
]


def _cutlist_record(row: CutListRow) -> List:
    return [
        row.designation,
        row.material,
        round(row.length, 1),
        round(row.width, 1),
        round(row.height, 1),
        row.count,
        round(row.total_length, 1),
        round(row.total_volume_m3, 6),
    ]


def cutlist_csv(file: BtlxFile) -> str:
    """Liste de débit au format CSV (en-tête inclus)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(_CUTLIST_HEADER)
    for row in cut_list(file):
        writer.writerow(_cutlist_record(row))
    return buffer.getvalue()


_PARTS_HEADER = [
    "number",
    "assembly",
    "designation",
    "material",
    "timber_grade",
    "count",
    "length_mm",
    "width_mm",
    "height_mm",
    "weight_kg",
    "volume_m3",
    "has_joinery",
]


def parts_csv(file: BtlxFile) -> str:
    """Liste détaillée des pièces (une ligne par <Part>) au format CSV."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(_PARTS_HEADER)
    for p in file.parts:
        writer.writerow(
            [
                p.number,
                p.assembly,
                p.designation,
                p.material,
                p.timber_grade,
                p.count,
                round(p.length, 1),
                round(p.width, 1),
                round(p.height, 1),
                p.weight if p.weight is not None else "",
                round(p.volume_m3, 6),
                "yes" if p.has_joinery else "no",
            ]
        )
    return buffer.getvalue()
