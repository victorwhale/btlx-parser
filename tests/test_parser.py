import pytest

import btlx
from btlx import BtlxParseError
from btlx.parser import parse_string

MINIMAL = '<BTLx xmlns="https://www.design2machine.com" Version="2.0"></BTLx>'

NO_NAMESPACE = """
<BTLx Version="1.0" Language="de">
  <Project Name="Ohne Namespace"/>
  <Parts>
    <Part Designation="Balken" Material="Spruce" Count="2"
          Length="3000" Width="100" Height="200"/>
  </Parts>
</BTLx>
"""

DIRECT_PROCESSINGS = """
<BTLx Version="2.0">
  <Parts>
    <Part Designation="X" Count="1" Length="1000" Width="50" Height="50">
      <ReferenceSide Side="1"/>
      <Drilling Name="Drilling" Diameter="8"/>
    </Part>
  </Parts>
</BTLx>
"""


def test_parse_file_version_and_language(doc):
    assert doc.version == "2.0"
    assert doc.language == "en"


def test_file_description(doc):
    fd = doc.file_description
    assert fd.file_name == "sample.btlx"
    assert fd.date == "2024-03-17"
    assert "roof" in fd.comment.lower() or "toiture" in fd.comment.lower()


def test_project(doc):
    assert "Mathis" in doc.project.name
    assert doc.project.comment


def test_parts_count(doc):
    assert len(doc.parts) == 3
    # total quantités : 8 + 3 + 24
    assert doc.part_count == 35


def test_part_typed_fields(doc):
    rafter = doc.parts[0]
    assert rafter.designation.startswith("Chevron")
    assert rafter.material == "Spruce"
    assert rafter.timber_grade == "C24"
    assert rafter.count == 8
    assert rafter.length == 4200.0
    assert rafter.width == 80.0
    assert rafter.height == 160.0
    assert rafter.weight == 34.4
    assert rafter.cross_section == "80x160"


def test_processings_parsed(doc):
    rafter = doc.parts[0]
    types = [p.type for p in rafter.processings]
    assert types == ["JackRafterCut", "JackRafterCut", "Drilling"]
    drilling = rafter.processings[2]
    assert drilling.param_float("Diameter") == 12.0
    assert drilling.param_int("Depth") == 80


def test_namespace_agnostic():
    doc = parse_string(NO_NAMESPACE)
    assert doc.language == "de"
    assert doc.parts[0].material == "Spruce"
    assert doc.parts[0].count == 2


def test_processings_without_wrapper():
    doc = parse_string(DIRECT_PROCESSINGS)
    part = doc.parts[0]
    # ReferenceSide est structurel → ignoré ; seul Drilling reste un usinage.
    assert [p.type for p in part.processings] == ["Drilling"]


def test_minimal_document_no_parts():
    doc = parse_string(MINIMAL)
    assert doc.parts == ()
    assert doc.part_count == 0


def test_empty_content_raises():
    with pytest.raises(BtlxParseError):
        parse_string("")
    with pytest.raises(BtlxParseError):
        parse_string("   ")


def test_malformed_xml_raises():
    with pytest.raises(BtlxParseError):
        parse_string("<BTLx><Parts></BTLx>")


def test_wrong_root_raises():
    with pytest.raises(BtlxParseError):
        parse_string("<NotBTLx/>")


def test_missing_file_raises(tmp_path):
    with pytest.raises(BtlxParseError):
        btlx.parse_file(tmp_path / "nope.btlx")
