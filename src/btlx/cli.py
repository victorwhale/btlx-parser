"""Interface en ligne de commande. / Command-line interface.

Usage:
    btlx fichier.btlx              # synthèse lisible / human summary
    btlx fichier.btlx --json      # JSON complet / full JSON
    btlx fichier.btlx --cutlist   # liste de débit CSV / cut list CSV
    btlx fichier.btlx -o out.json --json
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .aggregate import summary
from .errors import BtlxError
from .exporters import cutlist_csv, parts_csv, to_json
from .parser import parse_file, parse_string


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="btlx",
        description=(
            "Parser BTLx — charpente bois. / BTLx parser — timber construction. "
            "/ BTLx-Parser — Holzbau."
        ),
    )
    parser.add_argument(
        "file",
        help="Fichier .btlx, ou '-' pour stdin / .btlx file, or '-' for stdin",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--json", action="store_true", help="Sortie JSON complète / full JSON output"
    )
    group.add_argument(
        "--cutlist",
        action="store_true",
        help="Liste de débit CSV / cut list CSV / Stückliste CSV",
    )
    group.add_argument(
        "--parts",
        action="store_true",
        help="Liste détaillée des pièces CSV / detailed parts CSV",
    )
    group.add_argument(
        "--summary",
        action="store_true",
        help="Synthèse lisible (défaut) / human summary (default)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Écrire dans un fichier au lieu de stdout / write to file",
    )
    parser.add_argument(
        "--version", action="version", version=f"btlx {__version__}"
    )
    return parser


def _render_summary(doc) -> str:
    s = summary(doc)
    lines = [
        f"BTLx {s['version']}  —  {s['project'] or '(sans projet / no project)'}",
        f"  Pièces / Parts / Teile : {s['total_parts']} "
        f"({s['distinct_parts']} distinctes / distinct)",
        f"  Longueur / Length / Länge : {s['total_length_m']} m",
        f"  Volume : {s['total_volume_m3']} m³",
    ]
    if s["total_weight_kg"] is not None:
        lines.append(f"  Poids / Weight / Gewicht : {s['total_weight_kg']} kg")
    if s["materials"]:
        lines.append("  Matériaux / Materials / Materialien :")
        for mat, v in s["materials"].items():
            lines.append(
                f"    - {mat}: {v['count']}×  {v['volume_m3']} m³  {v['length_m']} m"
            )
    if s["processings"]:
        lines.append("  Usinages / Processings / Bearbeitungen :")
        for kind, n in s["processings"].items():
            lines.append(f"    - {kind}: {n}")
    return "\n".join(lines)


def _emit(text: str, output: Optional[str]) -> None:
    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(text if text.endswith("\n") else text + "\n")
    else:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.file == "-":
            doc = parse_string(sys.stdin.read())
        else:
            doc = parse_file(args.file)
    except BtlxError as exc:
        sys.stderr.write(f"Erreur / Error / Fehler : {exc}\n")
        return 2

    if args.json:
        _emit(to_json(doc), args.output)
    elif args.cutlist:
        _emit(cutlist_csv(doc), args.output)
    elif args.parts:
        _emit(parts_csv(doc), args.output)
    else:
        _emit(_render_summary(doc), args.output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
