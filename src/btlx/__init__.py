"""btlx — Parser BTLx pour l'industrie du bois / BTLx parser for the timber industry.

BTLx est le format d'échange ouvert (XML) des machines de charpente CNC
(Hundegger & autres). Ce paquet le transforme en données structurées,
exploitables par un humain comme par un agent.

Exemple / Example::

    import btlx

    doc = btlx.parse_file("chantier.btlx")
    print(doc.project.name, doc.part_count)
    print(btlx.to_json(doc))
    print(btlx.cutlist_csv(doc))
"""
from __future__ import annotations

from .aggregate import (
    CutListRow,
    cut_list,
    material_summary,
    processing_summary,
    summary,
    total_length_m,
    total_volume_m3,
    total_weight_kg,
)
from .errors import BtlxError, BtlxParseError
from .exporters import cutlist_csv, file_to_dict, part_to_dict, to_json
from .model import BtlxFile, FileDescription, Part, Processing, Project
from .parser import parse_file, parse_string

__version__ = "1.0.0"

__all__ = [
    "__version__",
    # parsing
    "parse_file",
    "parse_string",
    # modèle
    "BtlxFile",
    "FileDescription",
    "Project",
    "Part",
    "Processing",
    # agrégats
    "cut_list",
    "CutListRow",
    "summary",
    "material_summary",
    "processing_summary",
    "total_length_m",
    "total_volume_m3",
    "total_weight_kg",
    # exports
    "to_json",
    "cutlist_csv",
    "file_to_dict",
    "part_to_dict",
    # erreurs
    "BtlxError",
    "BtlxParseError",
]
