from __future__ import annotations

import math
import re
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")

__all__ = [
    "si_format",
    "si_parse",
]

# ============================================================================
# SI prefixes (including 2022 additions)
# ============================================================================


_SI_EXPONENTS = {
    -30: "q",  # quecto
    -27: "r",  # ronto
    -24: "y",  # yocto
    -21: "z",  # zepto
    -18: "a",  # atto
    -15: "f",  # femto
    -12: "p",  # pico
    -9: "n",  # nano
    -6: "µ",  # micro
    -3: "m",  # milli
    0: "",  # (none)
    3: "k",  # kilo
    6: "M",  # mega
    9: "G",  # giga
    12: "T",  # tera
    15: "P",  # peta
    18: "E",  # exa
    21: "Z",  # zetta
    24: "Y",  # yotta
    27: "R",  # ronna
    30: "Q",  # quetta
}

_SI_FACTORS = {prefix: 10.0**exp for exp, prefix in _SI_EXPONENTS.items()}

_MIN_EXPONENT = min(_SI_EXPONENTS)
_MAX_EXPONENT = max(_SI_EXPONENTS)

_FLOAT_PRESENTATION_TYPES = {"e", "E", "f", "F", "g", "G", "%"}

# ============================================================================
# Formatting
# ============================================================================


def _si_scale(value: float) -> tuple[float, str]:
    """
    Return (scaled_value, prefix).
    """

    if math.isnan(value) or math.isinf(value):
        return value, ""

    if value == 0:
        return 0.0, ""

    exponent = int(math.floor(math.log10(abs(value)) / 3) * 3)

    exponent = max(
        _MIN_EXPONENT,
        min(_MAX_EXPONENT, exponent),
    )

    scaled = value / (10**exponent)

    return scaled, _SI_EXPONENTS[exponent]


def _validate_format_spec(spec: str) -> None:
    """
    Allow only floating-point style formatting.
    """

    if not spec:
        return

    presentation_type = spec[-1]

    if presentation_type.isalpha() and presentation_type not in _FLOAT_PRESENTATION_TYPES:
        raise ValueError(
            f"unsupported format code {presentation_type!r} for SI formatting, use a floating-point style format code instead."
        )


class _SIFormatter:
    __slots__ = ("value",)

    def __init__(self, value: Any):
        self.value = value

    def __format__(self, spec: str) -> str:
        _validate_format_spec(spec)

        scaled, prefix = _si_scale(float(self.value))

        # Compact engineering representation.
        if not spec:
            spec = "g"

        return format(scaled, spec) + prefix

    def __str__(self) -> str:
        return format(self, "")

    def __repr__(self) -> str:
        return f"si_format({self.value!r})"


def si_format(value: Any) -> _SIFormatter:
    """
    Wrapper for SI-prefixed formatting.

    Examples:
        f"{si_format(10000)}"       -> "10k"
        f"{si_format(10000):.2f}"  -> "10.00k"
    """
    return _SIFormatter(value)


# ============================================================================
# Parsing
# ============================================================================

_PREFIX_CHARS = "".join(
    re.escape(prefix)
    for prefix in sorted(
        _SI_FACTORS,
        key=len,
        reverse=True,
    )
    if prefix
).replace("µ", "u")

_SI_NUMBER_RE = re.compile(
    rf"""
    ^
    \s*
    (?P<value>
        [+-]?
        (?:
            \d+(?:\.\d*)?
            |
            \.\d+
        )
        (?:[eE][+-]?\d+)?
    )
    \s*
    (?P<prefix>[{_PREFIX_CHARS}]?)
    \s*
    (?P<unit>[A-Za-z]*)?
    \s*
    $
    """,
    re.VERBOSE,
)


def _normalize_micro(text: str) -> str:
    return (
        text.replace("µ", "u").replace("μ", "u")  # U+00B5  # U+03BC
    )


def si_parse[T](
    text: str,
    numeric_type: Callable[[str], T] = float,
) -> T:
    """
    Parse an SI-prefixed value.

    Examples:
        si_parse("10k")           -> 10000.0
        si_parse("500m")          -> 0.5
        si_parse("2.5µ")          -> 2.5e-6
        si_parse("1R")            -> 1e27
        si_parse("4q")            -> 4e-30
        si_parse("10k", int)      -> 10000
        si_parse("2.5e3", int)    -> 2500
    """

    text = _normalize_micro(text.strip())

    match = _SI_NUMBER_RE.match(text)

    if not match:
        raise ValueError(f"invalid SI value: {text!r}")

    value = numeric_type(match.group("value"))
    prefix = match.group("prefix")

    factor = numeric_type(str(_SI_FACTORS[prefix]))

    return value * factor
