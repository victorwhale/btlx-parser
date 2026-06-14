"""Tests de durcissement XML (XXE / billion laughs)."""
import pytest

from btlx import BtlxParseError
from btlx.parser import parse_string

BILLION_LAUGHS = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;">
]>
<BTLx Version="2.0"><Parts/></BTLx>
"""

XXE = """<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<BTLx Version="2.0"><Project Name="&xxe;"/></BTLx>
"""


def test_billion_laughs_rejected():
    with pytest.raises(BtlxParseError):
        parse_string(BILLION_LAUGHS)


def test_xxe_external_entity_rejected():
    with pytest.raises(BtlxParseError):
        parse_string(XXE)
