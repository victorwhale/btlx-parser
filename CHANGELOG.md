# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.1.0]

### Added
- `Part.position` — reference point (X/Y/Z, mm) read from `<Transformations>`,
  useful for assembly placement.
- `Processing.category` — coarse family of each processing
  (`cut` / `drilling` / `joint` / `pocket` / `marking` / `other`) plus the
  `PROCESSING_CATEGORIES` mapping.
- `Part.processings_of(category)` and `Part.has_joinery` helpers.
- `parts_csv()` exporter — one detailed row per part.
- CLI `--parts` flag and stdin support (`btlx -`).
- `py.typed` marker (the package now ships type information).
- GitHub Actions CI matrix (Python 3.8 → 3.13).

### Changed
- `part_to_dict()` now includes `position`, `has_joinery`, and per-processing
  `category`.

## [1.0.0]

### Added
- Initial BTLx parser: namespace/version-agnostic parsing, immutable
  `BtlxFile` / `Part` / `Processing` model, cut list and volume/weight
  aggregates, JSON/CSV exports, CLI, XXE hardening.
