import math
from decimal import Decimal
from enum import IntEnum

import pytest

from engineering_format import si_format


def _fmt(value: float, spec: str = ".3f") -> str:
    """Format a value through si_format wrapper and return string output."""
    return format(si_format(value), spec)


SI_FORMAT_CASES = [
    (1e-30, "1.000q"),
    (4.2e-30, "4.200q"),
    (1e-27, "1.000r"),
    (6.6e-27, "6.600r"),
    (1e-24, "1.000y"),
    (5.5e-24, "5.500y"),
    (1e-21, "1.000z"),
    (3.2e-21, "3.200z"),
    (1e-18, "1.000a"),
    (2.5e-18, "2.500a"),
    (1e-15, "1.000f"),
    (7.8e-15, "7.800f"),
    (1e-12, "1.000p"),
    (4.2e-12, "4.200p"),
    (1e-9, "1.000n"),
    (9.9e-9, "9.900n"),
    (1e-6, "1.000µ"),
    (3.3e-6, "3.300µ"),
    (1e-3, "1.000m"),
    (5.5e-3, "5.500m"),
    (1e3, "1.000k"),
    (2.2e3, "2.200k"),
    (1e6, "1.000M"),
    (8.8e6, "8.800M"),
    (1e9, "1.000G"),
    (4.4e9, "4.400G"),
    (1e12, "1.000T"),
    (6.6e12, "6.600T"),
    (1e15, "1.000P"),
    (1.5e15, "1.500P"),
    (1e18, "1.000E"),
    (2.8e18, "2.800E"),
    (1e21, "1.000Z"),
    (3.5e21, "3.500Z"),
    (1e24, "1.000Y"),
    (9.9e24, "9.900Y"),
    (1e27, "1.000R"),
    (7.7e27, "7.700R"),
    (1e30, "1.000Q"),
    (8.8e30, "8.800Q"),
    # Exponents outside supported range should clamp at q/Q.
    (1e-33, "0.001q"),
    (5e-33, "0.005q"),
    (1e33, "1000.000Q"),
    (5e33, "5000.000Q"),
    # Special cases like zero, negative sign.
    (0.0, "0.000"),
    (-1.0, "-1.000"),
    (-1e-6, "-1.000µ"),
]


@pytest.mark.parametrize("value, expected", SI_FORMAT_CASES)
def test_si_format_vector(value: float, expected: str):
    """Format vector coverage for all SI prefixes with a fixed numeric spec."""
    assert _fmt(value) == expected
    assert _fmt(Decimal(value)) == expected


SPEC_CASES = [
    (10000.0, "", "10k"),
    (1234.0, ".2f", "1.23k"),
    (1234.0, ".1f", "1.2k"),
    (1234.0, ".3g", "1.23k"),
    (1234.0, ".2E", "1.23E+00k"),
    (1234.0, ".2F", "1.23k"),
    (1234.0, ".3G", "1.23k"),
    (0.0012, ".1e", "1.2e+00m"),
    (1, "g", "1"),
    (1, ".2%", "100.00%"),
    (1234.0, "+.2f", "+1.23k"),
    (1234.0, " .2f", " 1.23k"),
    (1000.0, "#.0f", "1.k"),
    (1000.0, "#.3g", "1.00k"),
    (1000.0, "10.3f", "    1.000k"),
    (1000.0, "010.3f", "00001.000k"),
    (1000.0, "03.3f", "1.000k"),
    (-1000.0, "=+010.3f", "-00001.000k"),
    (-1000.0, "010.3f", "-0001.000k"),
    (1000.0, "<10.3f", "1.000k    "),
    (1000.0, "^10.3f", "  1.000k  "),
    (1000.0, "*>10.3f", "****1.000k"),
    (1e33, ",.1f", "1,000.0Q"),
    (1e33, "_.1f", "1_000.0Q"),
]


@pytest.mark.parametrize("value, spec, expected", SPEC_CASES)
def test_si_format_specs(value: float, spec: str, expected: str):
    """Verify output with different valid format specs, including empty spec."""
    assert _fmt(value, spec) == expected


def test_si_format_no_prefix_symbol_reserves_width_column():
    prefixed = format(si_format(1000), "10.3f")
    unprefixed = format(si_format(1, no_prefix_symbol=" "), "10.3f")

    assert prefixed == "    1.000k"
    assert unprefixed == "    1.000 "
    assert prefixed.index("1") == unprefixed.index("1")


def test_si_format_no_prefix_symbol_with_equal_alignment():
    assert format(si_format(1, no_prefix_symbol=" "), "=+010.3f") == "+00001.000 "


def test_si_format_no_prefix_symbol_without_width():
    assert format(si_format(1, no_prefix_symbol=" "), ".3f") == "1.000 "


@pytest.mark.parametrize(
    "value, expected",
    [
        (0.0, "0.000 "),
        (1.0, "1.000 "),
        (-999.0, "-999.000 "),
        (float("nan"), "nan "),
        (float("inf"), "inf "),
        (float("-inf"), "-inf "),
    ],
)
def test_si_format_no_prefix_symbol_for_empty_prefix_values(value: float, expected: str):
    assert format(si_format(value, no_prefix_symbol=" "), ".3f") == expected


@pytest.mark.parametrize(
    "spec, expected",
    [
        ("<10.3f", "1.000     "),
        ("^10.3f", "  1.000   "),
        ("*>10.3f", "****1.000 "),
    ],
)
def test_si_format_no_prefix_symbol_with_alignment(spec: str, expected: str):
    assert format(si_format(1, no_prefix_symbol=" "), spec) == expected


def test_si_format_no_prefix_symbol_is_ignored_for_prefixed_values():
    assert format(si_format(1000, no_prefix_symbol=" "), "10.3f") == "    1.000k"


@pytest.mark.parametrize(
    "value, spec, scaled, prefix",
    [
        (1234.0, ".2n", 1.234, "k"),
        (-1234.0, ".3n", -1.234, "k"),
    ],
)
def test_si_format_n_specs(value: float, spec: str, scaled: float, prefix: str):
    """`n` formatting is locale-aware; derive expected text from runtime locale behavior."""
    expected = format(scaled, spec) + prefix
    assert _fmt(value, spec) == expected


INVALID_SPEC_CASES = [
    "d",
    "s",
    "a",
    "A",
    "b",
    "c",
    "o",
    "x",
    "X",
    "10.2ff",
    "10..2f",
    ".-2f",
    ",_.2f",
]


@pytest.mark.parametrize("spec", INVALID_SPEC_CASES)
def test_si_format_invalid_specs(spec: str):
    """Non-floating presentation specs should be rejected."""
    with pytest.raises(ValueError):
        _fmt(1.23, spec)


def test_si_format_nan():
    """Test with NaN (Not a Number)."""
    result = _fmt(float("nan"), "f")
    assert result == "nan" or math.isnan(float(result))


def test_si_format_positive_infinity():
    """Test with positive infinity."""
    result = _fmt(float("inf"), "f")
    assert result == "inf" or result == "+inf"


def test_si_format_negative_infinity():
    """Test with negative infinity."""
    result = _fmt(float("-inf"), "f")
    assert result == "-inf"


INT_FORMAT_CASES = [
    (0, "0.000"),
    (1, "1.000"),
    (-1, "-1.000"),
    (999, "999.000"),
    (1000, "1.000k"),
    (-1200, "-1.200k"),
    (1_000_000, "1.000M"),
    (2_147_483_647, "2.147G"),
]


@pytest.mark.parametrize("value, expected", INT_FORMAT_CASES)
def test_si_format_int_values(value: int, expected: str):
    """Built-in ints should format with SI prefixes and configured precision."""
    assert _fmt(value) == expected


class _CustomInt(int):
    pass


class _Scale(IntEnum):
    BASE = 1
    KILO = 1000


@pytest.mark.parametrize(
    "value, expected",
    [
        (_CustomInt(1), "1.000"),
        (_CustomInt(1000), "1.000k"),
        (_Scale.BASE, "1.000"),
        (_Scale.KILO, "1.000k"),
    ],
)
def test_si_format_int_like_types(value: int, expected: str):
    """Int-derived values should behave the same as plain int."""
    assert _fmt(value) == expected


def test_si_format_str_uses_default_format_spec():
    """__str__ delegates to __format__("") and defaults to compact engineering format."""
    assert str(si_format(1000)) == "1k"
    assert str(si_format(0.001)) == "1m"


def test_si_format_repr_for_int_and_decimal():
    """__repr__ should expose constructor-style wrapper representation."""
    assert repr(si_format(1000)) == "si_format(1000)"
    assert repr(si_format(Decimal("1.25"))) == "si_format(Decimal('1.25'))"
