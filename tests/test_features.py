"""Tests des ajouts 1.1 : position, catégories, parts CSV, stdin."""
import csv
import io
import json

from btlx import parts_csv
from btlx.cli import main
from btlx.model import Position
from btlx.parser import parse_string

NO_TRANSFORM = """
<BTLx Version="2.0">
  <Parts>
    <Part Designation="X" Count="1" Length="1000" Width="50" Height="50"/>
  </Parts>
</BTLx>
"""


def test_position_parsed(doc):
    rafter = doc.parts[0]
    assert isinstance(rafter.position, Position)
    assert rafter.position.x == 0.0
    assert rafter.position.y == 0.0
    assert rafter.position.z == 0.0


def test_position_absent_is_none():
    doc = parse_string(NO_TRANSFORM)
    assert doc.parts[0].position is None


def test_position_partial_transformations_is_none():
    # <Transformations> présent mais incomplet à divers niveaux → None.
    for inner in (
        "",
        "<Transformation/>",
        "<Transformation><Position/></Transformation>",
    ):
        xml = (
            '<BTLx Version="2.0"><Parts><Part Count="1" Length="1" '
            f'Width="1" Height="1"><Transformations>{inner}</Transformations>'
            "</Part></Parts></BTLx>"
        )
        assert parse_string(xml).parts[0].position is None


def test_processing_categories(doc):
    rafter = doc.parts[0]
    assert rafter.processings[0].category == "cut"  # JackRafterCut
    assert rafter.processings[2].category == "drilling"  # Drilling
    purlin = doc.parts[1]
    assert purlin.processings_of("joint")  # Lap + Mortise
    assert purlin.has_joinery is True


def test_unknown_processing_is_other():
    doc = parse_string(
        '<BTLx Version="2.0"><Parts><Part Count="1" Length="1" '
        'Width="1" Height="1"><Processings><Frobnicate Name="x"/>'
        "</Processings></Part></Parts></BTLx>"
    )
    proc = doc.parts[0].processings[0]
    assert proc.category == "other"
    assert doc.parts[0].has_joinery is False


def test_parts_csv(doc):
    rows = list(csv.reader(io.StringIO(parts_csv(doc))))
    assert rows[0][0] == "number"
    assert len(rows) == 1 + 3  # une ligne par pièce
    # La panne (ligne 2) a de l'assemblage.
    purlin = rows[2]
    assert purlin[2].startswith("Panne")
    assert purlin[-1] == "yes"  # has_joinery


def test_part_to_dict_includes_new_fields(doc):
    from btlx import part_to_dict

    d = part_to_dict(doc.parts[0])
    assert d["position"] == {"x": 0.0, "y": 0.0, "z": 0.0}
    assert d["has_joinery"] is False  # chevron : coupes + perçage, pas d'assemblage
    assert d["processings"][0]["category"] == "cut"


def test_cli_parts(capsys, sample_path):
    code = main([str(sample_path), "--parts"])
    out = capsys.readouterr().out
    assert code == 0
    assert out.splitlines()[0].startswith("number")


def test_cli_stdin(capsys, sample_path, monkeypatch):
    import sys

    monkeypatch.setattr(sys, "stdin", io.StringIO(sample_path.read_text()))
    code = main(["-", "--json"])
    out = capsys.readouterr().out
    assert code == 0
    assert json.loads(out)["summary"]["total_parts"] == 35
