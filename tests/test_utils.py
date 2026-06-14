from btlx._utils import to_float, to_int


def test_to_float_comma_decimal():
    assert to_float("1,5") == 1.5


def test_to_float_invalid_returns_default():
    assert to_float("abc", 0.0) == 0.0
    assert to_float(None) is None
    assert to_float("") is None
    assert to_float("   ", 9.0) == 9.0


def test_to_int_from_float_string():
    assert to_int("3.0") == 3


def test_to_int_invalid_returns_default():
    assert to_int("xyz", 1) == 1
    assert to_int(None) is None
    assert to_int("") is None
