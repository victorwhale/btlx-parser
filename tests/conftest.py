from pathlib import Path

import pytest

import btlx

SAMPLE = Path(__file__).resolve().parent.parent / "examples" / "sample.btlx"


@pytest.fixture
def sample_path() -> Path:
    return SAMPLE


@pytest.fixture
def doc():
    return btlx.parse_file(SAMPLE)
