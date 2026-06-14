import math

from btlx import (
    cut_list,
    material_summary,
    processing_summary,
    summary,
    total_length_m,
    total_volume_m3,
    total_weight_kg,
)
from btlx.parser import parse_string

DUP = """
<BTLx Version="2.0">
  <Parts>
    <Part Designation="A" Material="Spruce" Count="2" Length="1000" Width="100" Height="100"/>
    <Part Designation="A" Material="Spruce" Count="3" Length="1000" Width="100" Height="100"/>
    <Part Designation="B" Material="Oak" Count="1" Length="2000" Width="50" Height="50"/>
  </Parts>
</BTLx>
"""

NO_WEIGHT = """
<BTLx Version="2.0">
  <Parts>
    <Part Designation="A" Count="1" Length="1000" Width="100" Height="100"/>
  </Parts>
</BTLx>
"""


def test_cut_list_groups_identical_parts():
    rows = cut_list(parse_string(DUP))
    # A regroupé (2+3), B séparé
    assert len(rows) == 2
    a, b = rows
    assert a.designation == "A"
    assert a.count == 5
    assert a.total_length == 5000.0
    assert b.designation == "B"
    assert b.count == 1


def test_total_volume(doc):
    # 8×(4.2×0.08×0.16) + 3×(6.0×0.12×0.24) + 24×(2.6×0.06×0.12)
    expected = (
        8 * (4.2 * 0.08 * 0.16)
        + 3 * (6.0 * 0.12 * 0.24)
        + 24 * (2.6 * 0.06 * 0.12)
    )
    assert math.isclose(total_volume_m3(doc), expected, rel_tol=1e-9)


def test_total_length_m(doc):
    expected = (8 * 4200 + 3 * 6000 + 24 * 2600) / 1000.0
    assert math.isclose(total_length_m(doc), expected, rel_tol=1e-9)


def test_total_weight_present(doc):
    expected = 8 * 34.4 + 3 * 103.7 + 24 * 11.2
    assert math.isclose(total_weight_kg(doc), expected, rel_tol=1e-9)


def test_total_weight_absent_returns_none():
    assert total_weight_kg(parse_string(NO_WEIGHT)) is None


def test_material_summary(doc):
    ms = material_summary(doc)
    assert set(ms) == {"Spruce", "Glulam GL24h"}
    assert ms["Spruce"]["count"] == 8 + 24


def test_processing_summary(doc):
    ps = processing_summary(doc)
    assert ps["JackRafterCut"] == 2
    assert ps["Drilling"] == 1
    assert ps["Mortise"] == 1
    assert ps["Tenon"] == 1


def test_summary_shape(doc):
    s = summary(doc)
    assert s["distinct_parts"] == 3
    assert s["total_parts"] == 35
    assert s["total_weight_kg"] is not None
    assert "Spruce" in s["materials"]
