from decimal import Decimal
from enum import IntEnum

import pytest

from engineering_format import si_parse


class _CustomInt(int):
    pass


class _Scale(IntEnum):
    BASE = 1
    KILO = 1000


PARSE_CASES = [
    ("1q", 1e-30),
    ("2r", 2e-27),
    ("3y", 3e-24),
    ("4z", 4e-21),
    ("5a", 5e-18),
    ("6f", 6e-15),
    ("7p", 7e-12),
    ("8n", 8e-9),
    ("9µ", 9e-6),
    ("9u", 9e-6),
    ("9μ", 9e-6),
    ("10m", 10e-3),
    ("11", 11.0),
    ("12k", 12e3),
    ("13M", 13e6),
    ("14G", 14e9),
    ("15T", 15e12),
    ("16P", 16e15),
    ("17E", 17e18),
    ("18Z", 18e21),
    ("19Y", 19e24),
    ("20R", 20e27),
    ("21Q", 21e30),
    ("  2.5k  ", 2500.0),
    (".5k", 500.0),
    ("1.2e3", 1200.0),
    ("1.2e-3k", 1.2),
    # Current parser should ignore trailing text.
    ("1kk", 1000.0),
    ("1e", 1.0),
    ("1k-", 1000.0),
    ("1k2", 1000.0),
    ("1m/s", 0.001),
    # support for underscores in numeric literals (PEP 515)
    ("1_000", 1000.0),
    ("1_000k", 1000000.0),
    # space between number and SI prefix
    ("9 n", 9e-9),
    ("10 m", 10e-3),
    ("12 k", 12e3),
    ("13 M", 13e6),
    ("14 G", 14e9),
]


@pytest.mark.parametrize("text, expected", PARSE_CASES)
def test_si_parse_vector(text: str, expected: float):
    """Parse SI-prefixed values across legacy and 2022 prefixes."""
    assert si_parse(text) == pytest.approx(expected)


@pytest.mark.parametrize(
    "text, numeric_type, expected",
    [
        ("3M", Decimal, Decimal(3000000)),
        ("2.5m", Decimal, Decimal("0.0025")),
        ("10k", int, 10000),
        ("2.5e3", int, 2500),
        ("1", int, 1),
        ("500m", int, 0),
        ("1.2e-3k", int, 1),
        ("1", _CustomInt, _CustomInt(1)),
        ("10k", _CustomInt, _CustomInt(10000)),
        ("1", _Scale, _Scale.BASE),
        ("1k", _Scale, _Scale.KILO),
    ],
)
def test_si_parse_numeric_type(text: str, numeric_type, expected):
    """numeric_type controls output type and conversion semantics."""
    result = si_parse(text, numeric_type)
    assert result == expected
    assert isinstance(result, numeric_type)


@pytest.mark.parametrize(
    "text",
    [
        "",
        " ",
        "abc",
        "k10",
        "1.2.3k",
        "--1k",
    ],
)
def test_si_parse_invalid_values(text: str):
    """Invalid SI strings should raise ValueError."""
    with pytest.raises(ValueError):
        si_parse(text)
