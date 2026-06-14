import csv
import io
import json

from btlx import cutlist_csv, file_to_dict, part_to_dict, to_json


def test_to_json_roundtrip(doc):
    payload = json.loads(to_json(doc))
    assert payload["version"] == "2.0"
    assert len(payload["parts"]) == 3
    assert payload["summary"]["total_parts"] == 35


def test_part_to_dict(doc):
    d = part_to_dict(doc.parts[0])
    assert d["designation"].startswith("Chevron")
    assert d["cross_section"] == "80x160"
    assert d["processings"][2]["type"] == "Drilling"
    assert d["attrs"]["TimberGrade"] == "C24"


def test_file_to_dict_has_summary(doc):
    d = file_to_dict(doc)
    assert d["project"]["name"].startswith("Maison")
    assert "summary" in d


def test_cutlist_csv_parses(doc):
    text = cutlist_csv(doc)
    rows = list(csv.reader(io.StringIO(text)))
    header = rows[0]
    assert header[0] == "designation"
    assert "total_volume_m3" in header
    # 3 pièces distinctes → 3 lignes de données
    assert len(rows) == 1 + 3
    body = rows[1]
    assert body[0].startswith("Chevron")
    assert body[5] == "8"  # count
