import json

import pytest

from btlx.cli import main


def test_cli_summary(capsys, sample_path):
    code = main([str(sample_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "BTLx 2.0" in out
    assert "Mathis" in out
    assert "m³" in out


def test_cli_json(capsys, sample_path):
    code = main([str(sample_path), "--json"])
    out = capsys.readouterr().out
    assert code == 0
    payload = json.loads(out)
    assert payload["summary"]["total_parts"] == 35


def test_cli_cutlist(capsys, sample_path):
    code = main([str(sample_path), "--cutlist"])
    out = capsys.readouterr().out
    assert code == 0
    assert out.splitlines()[0].startswith("designation")


def test_cli_output_file(tmp_path, sample_path):
    target = tmp_path / "out.json"
    code = main([str(sample_path), "--json", "-o", str(target)])
    assert code == 0
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["version"] == "2.0"


def test_cli_error_on_missing_file(capsys, tmp_path):
    code = main([str(tmp_path / "absent.btlx")])
    err = capsys.readouterr().err
    assert code == 2
    assert "Erreur" in err


def test_cli_mutually_exclusive(sample_path):
    with pytest.raises(SystemExit):
        main([str(sample_path), "--json", "--cutlist"])
