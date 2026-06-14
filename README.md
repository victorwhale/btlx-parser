# btlx-parser

[![CI](https://github.com/victorwhale/btlx-parser/actions/workflows/ci.yml/badge.svg)](https://github.com/victorwhale/btlx-parser/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> 🇩🇪 [Deutsch](#deutsch) · 🇬🇧 [English](#english) · 🇫🇷 [Français](#français)

A tiny, dependency-free **BTLx parser** for the timber-construction industry.
BTLx is the open XML exchange format used by CNC carpentry machines (Hundegger
and others, [design2machine.com](https://www.design2machine.com)). This library
turns `.btlx` files into clean, structured data — parts, processings, cut lists,
volumes — usable by a human or an agent.

```bash
pip install btlx-parser
btlx my-roof.btlx --cutlist
```

- ✅ Zero runtime dependencies (Python stdlib only)
- ✅ Namespace- and version-agnostic (BTLx 1.x / 2.x)
- ✅ Hardened against XXE / billion-laughs attacks
- ✅ Library **and** command-line tool (reads files or stdin)
- ✅ Typed model with part **positions** and processing **categories**
- ✅ Exports: structured `dict`, JSON, CSV cut list, CSV parts list
- ✅ Typed package (`py.typed`), 99% test coverage, MIT licensed

---

## Deutsch

### Was ist das?

**btlx-parser** liest BTLx-Dateien (das offene XML-Austauschformat für
CNC-Abbundmaschinen im Holzbau) und wandelt sie in strukturierte Daten um:
Bauteile, Bearbeitungen, Stücklisten, Volumen und Gewichte.

### Installation

```bash
pip install btlx-parser
# optional, härtere XML-Sicherheit / stärkerer XXE-Schutz:
pip install "btlx-parser[secure]"
```

### Kommandozeile

```bash
btlx datei.btlx              # Lesbare Zusammenfassung
btlx datei.btlx --cutlist    # Stückliste als CSV
btlx datei.btlx --json       # Vollständiges JSON
btlx datei.btlx --json -o out.json
```

### Als Bibliothek

```python
import btlx

doc = btlx.parse_file("datei.btlx")
print(doc.project.name, doc.part_count)            # Projektname, Teileanzahl

for teil in doc.parts:
    print(teil.designation, teil.cross_section, teil.length, "mm")
    for bearbeitung in teil.processings:
        print("  ", bearbeitung.type, bearbeitung.params)

print(btlx.to_json(doc))        # alles als JSON
print(btlx.cutlist_csv(doc))    # Stückliste als CSV
```

### Begriffe (Feldname → Bedeutung)

| Feld | Bedeutung |
|------|-----------|
| `length` / `width` / `height` | Maße in **Millimeter** |
| `count` | Stückzahl des Bauteils |
| `material`, `timber_grade` | Holzart, Festigkeitsklasse (z. B. C24, GL24h) |
| `volume_m3` | Volumen pro Stück in m³ |
| `processings` | Bearbeitungen (Schnitt, Bohrung, Zapfen, Schlitz …) |

---

## English

### What is it?

**btlx-parser** reads BTLx files — the open XML exchange format for CNC
carpentry machines in timber construction — and turns them into structured
data: parts, processings, cut lists, volumes and weights.

### Why?

BTLx is a great machine format, but it is verbose XML with ~40 processing types
and optional namespaces. This parser gives you:

- a **stable, typed data model** for the fields that matter on a cut list, plus
- the **raw attribute bag** for everything else, so it never silently drops data.

That makes it equally good for a spreadsheet export, a cost estimate, or feeding
a BTLx file to an LLM agent.

### Installation

```bash
pip install btlx-parser
# optional hardened XML stack (defusedxml):
pip install "btlx-parser[secure]"
```

### Command line

```bash
btlx file.btlx              # human-readable summary (default)
btlx file.btlx --cutlist    # grouped cut list as CSV
btlx file.btlx --parts      # detailed parts list as CSV
btlx file.btlx --json       # full structured JSON
btlx file.btlx --json -o out.json
cat file.btlx | btlx -      # read from stdin
```

### As a library

```python
import btlx

doc = btlx.parse_file("file.btlx")     # or btlx.parse_string(xml_text)

print(doc.version, doc.project.name, doc.part_count)

for part in doc.parts:
    print(part.designation, part.cross_section, part.length, "mm")
    print("  volume:", part.volume_m3, "m³  weight:", part.weight, "kg")
    print("  position:", part.position)        # ReferencePoint X/Y/Z in mm, or None
    print("  needs joinery:", part.has_joinery)
    for proc in part.processings:
        # proc.type e.g. "JackRafterCut", "Drilling", "Mortise", "Tenon"
        # proc.category e.g. "cut", "drilling", "joint", "pocket", "marking"
        print("  ", proc.category, proc.type, proc.param_float("Angle"))

# Aggregates
print(btlx.total_volume_m3(doc))       # total timber volume (m³)
print(btlx.material_summary(doc))      # per-material breakdown
print(btlx.summary(doc))               # JSON-ready summary dict

# Exports
print(btlx.to_json(doc))               # full document as JSON
print(btlx.cutlist_csv(doc))           # grouped cut list as CSV
print(btlx.parts_csv(doc))             # detailed parts list as CSV
```

### Data model

| Object | Key fields |
|--------|-----------|
| `BtlxFile` | `version`, `language`, `project`, `parts`, `part_count` |
| `Part` | `designation`, `material`, `timber_grade`, `count`, `length`/`width`/`height` (mm), `weight` (kg), `volume_m3`, `cross_section`, `processings`, `attrs` (raw) |
| `Processing` | `type`, `name`, `params` (raw attrs), `param_float()`, `param_int()` |
| `CutListRow` | `designation`, `material`, dims, `count`, `total_length`, `total_volume_m3` |

All objects are **immutable** (frozen dataclasses); lengths are in millimetres,
volumes in m³, weights in kg.

### Error handling & security

- Any malformed XML, missing file, or non-`<BTLx>` root raises `BtlxParseError`.
- DTD/entity declarations are **rejected** to block XXE and billion-laughs
  attacks, even with the stdlib parser. Install `[secure]` for `defusedxml` too.

---

## Français

### C'est quoi ?

**btlx-parser** lit les fichiers BTLx — le format d'échange XML ouvert des
machines de taille à commande numérique (CNC) en charpente bois — et les
transforme en données structurées : pièces, usinages, listes de débit, volumes
et poids.

### Pourquoi ?

BTLx est un excellent format machine, mais c'est du XML verbeux avec ~40 types
d'usinage et des espaces de noms optionnels. Ce parser fournit :

- un **modèle de données typé et stable** pour les champs utiles d'une liste de
  débit, plus
- le **dictionnaire d'attributs bruts** pour tout le reste, sans jamais perdre
  silencieusement de données.

Idéal pour un export tableur, un métré, ou pour donner un fichier BTLx à manger
à un agent LLM.

### Installation

```bash
pip install btlx-parser
# pile XML durcie en option (defusedxml) :
pip install "btlx-parser[secure]"
```

### Ligne de commande

```bash
btlx fichier.btlx              # synthèse lisible (par défaut)
btlx fichier.btlx --cutlist    # liste de débit en CSV
btlx fichier.btlx --json       # JSON structuré complet
btlx fichier.btlx --json -o sortie.json
```

### En bibliothèque

```python
import btlx

doc = btlx.parse_file("fichier.btlx")   # ou btlx.parse_string(texte_xml)

print(doc.version, doc.project.name, doc.part_count)

for piece in doc.parts:
    print(piece.designation, piece.cross_section, piece.length, "mm")
    print("  volume :", piece.volume_m3, "m³  poids :", piece.weight, "kg")
    for usinage in piece.processings:
        # usinage.type ex. "JackRafterCut", "Drilling", "Mortise", "Tenon"
        print("  ", usinage.type, usinage.param_float("Angle"))

# Agrégats
print(btlx.total_volume_m3(doc))        # volume total de bois (m³)
print(btlx.material_summary(doc))       # ventilation par matériau
print(btlx.summary(doc))                # dictionnaire de synthèse (prêt JSON)

# Exports
print(btlx.to_json(doc))                # document complet en JSON
print(btlx.cutlist_csv(doc))            # liste de débit regroupée en CSV
```

### Modèle de données

| Objet | Champs clés |
|-------|-------------|
| `BtlxFile` | `version`, `language`, `project`, `parts`, `part_count` |
| `Part` | `designation`, `material`, `timber_grade`, `count`, `length`/`width`/`height` (mm), `weight` (kg), `volume_m3`, `cross_section`, `processings`, `attrs` (brut) |
| `Processing` | `type`, `name`, `params` (attributs bruts), `param_float()`, `param_int()` |
| `CutListRow` | `designation`, `material`, dimensions, `count`, `total_length`, `total_volume_m3` |

Tous les objets sont **immuables** (dataclasses gelées) ; les longueurs sont en
millimètres, les volumes en m³, les poids en kg.

### Gestion des erreurs & sécurité

- Tout XML mal formé, fichier absent ou racine non-`<BTLx>` lève `BtlxParseError`.
- Les déclarations DTD/entités sont **refusées** pour bloquer les attaques XXE et
  « billion laughs », même avec le parser standard. Installez `[secure]` pour
  ajouter `defusedxml`.

---

## Development

```bash
git clone https://github.com/victorwhale/btlx-parser
cd btlx-parser
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest --cov=btlx          # 37 tests, ~99% coverage
```

A demo file lives in [`examples/sample.btlx`](examples/sample.btlx).

## License

MIT — see [LICENSE](LICENSE). Contributions welcome.

BTLx is a format by [design2machine.com](https://www.design2machine.com); this
project is an independent, unofficial parser.
