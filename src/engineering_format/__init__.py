"""SI/metric prefix formatting and parsing for Python.

Formatting is exposed through Python's standard format protocol, so SI prefixes
work seamlessly with f-strings and :func:`format` without altering numeric types::

    >>> from engineering_format import si_format
    >>> f"{si_format(4700):.2f}"
    '4.70k'

Units are deliberately not supported; append them in the surrounding format string::

    >>> f"{si_format(4700):.2f} Ω"
    '4.70k Ω'

Parsing is the inverse::

    >>> from engineering_format import si_parse
    >>> si_parse("4.70k")
    4700.0
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable
from decimal import Decimal
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
# Accept plain ASCII "u" as an alias for the micro sign.
_SI_FACTORS["u"] = _SI_FACTORS["µ"]

_MIN_EXPONENT = min(_SI_EXPONENTS)
_MAX_EXPONENT = max(_SI_EXPONENTS)

_FLOAT_PRESENTATION_TYPES = {"e", "E", "f", "F", "g", "G", "n", "%"}

_FORMAT_SPEC_RE = re.compile(
    r"""
    ^
    (?:(?P<fill>.)?(?P<align>[<>=^]))?
    (?P<sign>[+\- ])?
    (?P<alternate>\#)?
    (?P<zero>0)?
    (?P<width>\d+)?
    (?P<grouping_option>[_,])?
    (?P<precision>\.\d+)?
    (?P<presentation_type>[a-zA-Z%])?
    $
    """,
    re.VERBOSE,
)

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


def _parse_format_spec(spec: str) -> dict[str, str | bool | int | None]:
    match = _FORMAT_SPEC_RE.fullmatch(spec)

    if not match:
        raise ValueError(f"invalid format specifier: {spec!r}")

    groups = match.groupdict()

    return {
        "fill": groups["fill"],
        "align": groups["align"],
        "sign": groups["sign"],
        "alternate": bool(groups["alternate"]),
        "zero": bool(groups["zero"]),
        "width": int(groups["width"]) if groups["width"] else None,
        "grouping_option": groups["grouping_option"],
        "precision": groups["precision"],
        "presentation_type": groups["presentation_type"],
    }


def _build_numeric_spec(parsed_spec: dict[str, str | bool | int | None]) -> str:
    parts: list[str] = []

    sign = parsed_spec["sign"]
    alternate = parsed_spec["alternate"]
    grouping_option = parsed_spec["grouping_option"]
    precision = parsed_spec["precision"]
    presentation_type = parsed_spec["presentation_type"]

    if sign:
        parts.append(str(sign))
    if alternate:
        parts.append("#")
    if grouping_option:
        parts.append(str(grouping_option))
    if precision:
        parts.append(str(precision))
    if presentation_type:
        parts.append(str(presentation_type))

    return "".join(parts)


def _apply_layout(
    rendered: str,
    parsed_spec: dict[str, str | bool | int | None],
) -> str:
    width = parsed_spec["width"]

    if not width:
        return rendered

    fill = parsed_spec["fill"] or " "
    align = parsed_spec["align"]

    if align in ("<", ">", "^"):
        return format(rendered, f"{fill}{align}{width}")

    if parsed_spec["zero"]:
        padding = width - len(rendered)

        if padding <= 0:
            return rendered

        if rendered and rendered[0] in "+-":
            return rendered[0] + ("0" * padding) + rendered[1:]

        return ("0" * padding) + rendered

    return format(rendered, f">{width}")


class _SIFormatter:
    """Wrapper returned by :func:`si_format`.

    Interact with this object exclusively through :func:`format` or f-strings;
    do not instantiate it directly.

    >>> obj = si_format(1500)
    >>> f"{obj:.2f}"
    '1.50k'
    >>> format(obj, '.2f')
    '1.50k'
    """

    __slots__ = ("value",)

    def __init__(self, value: Any):
        self.value = value

    def __format__(self, spec: str) -> str:
        """Format the value with an SI prefix using a standard Python float format spec.

        The *spec* follows the standard format mini-language::

            [[fill]align][sign][#][0][width][grouping_option][.precision][type]

        Supported presentation types: ``e``, ``E``, ``f``, ``F``, ``g``, ``G``,
        ``n``, ``%``, and empty (defaults to ``g``).

        The SI prefix is appended to the formatted number *before* padding, so
        *width* and alignment account for the prefix character:

        >>> format(si_format(1000), '10.3f')
        '    1.000k'
        >>> format(si_format(1000), '<10.3f')
        '1.000k    '
        >>> format(si_format(1000), '^10.3f')
        '  1.000k  '
        >>> format(si_format(1000), '*>10.3f')
        '****1.000k'
        >>> format(si_format(1000), '010.3f')
        '00001.000k'
        >>> format(si_format(-1000), '=+010.3f')
        '-00001.000k'

        Raises:
            ValueError: If a non-float presentation type (e.g. ``d``, ``s``) is used.
        """
        _validate_format_spec(spec)

        scaled, prefix = _si_scale(float(self.value))

        # Compact engineering representation.
        if not spec:
            spec = "g"

        parsed_spec = _parse_format_spec(spec)

        # Keep explicit '=' behavior numeric-first to preserve existing expectations.
        if parsed_spec["align"] == "=":
            return format(scaled, spec) + prefix

        numeric_spec = _build_numeric_spec(parsed_spec)
        rendered = format(scaled, numeric_spec) + prefix

        return _apply_layout(rendered, parsed_spec)

    def __str__(self) -> str:
        """Equivalent to ``format(self, '')`` — compact ``g``-style with SI prefix."""
        return format(self, "")

    def __repr__(self) -> str:
        """Developer representation showing the wrapped value."""
        return f"si_format({self.value!r})"


def si_format(value: Any) -> _SIFormatter:
    """Wrap *value* for SI-prefixed formatting via f-strings or :func:`format`.

    Returns a :class:`_SIFormatter` whose ``__format__`` method selects the
    appropriate SI prefix (quecto ``q`` through quetta ``Q``) and appends it
    to the formatted number.  All standard float format-spec options —
    precision, width, fill, alignment, sign, grouping — are honoured; the
    prefix is included within the specified *width*.

    Units are intentionally not supported.  Append them outside the format
    expression::

        >>> f"{si_format(4700):.2f} Ω"
        '4.70k Ω'

    Args:
        value: Any value accepted by :func:`float`, including :class:`int`,
            :class:`float`, and :class:`~decimal.Decimal`.

    Returns:
        A :class:`_SIFormatter` object.  Use it with :func:`format` or inside
        an f-string format expression; do not call it directly.

    Examples:

        >>> f"{si_format(10_000)}"
        '10k'
        >>> f"{si_format(10_000):.2f}"
        '10.00k'
        >>> f"{si_format(0.0047):.1f}"
        '4.7m'
        >>> f"{si_format(2.5e-9):.3g}"
        '2.5n'
        >>> f"{si_format(1e-6):.2f}"
        '1.00µ'
        >>> format(si_format(1000), '+.2f')
        '+1.00k'
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
)

_SI_VALUE_PATTERN = r"""
    [+-]?
    (?:
        \d(?:_?\d)*(?:\.(?:\d(?:_?\d)*)?)?
        |
        \.\d(?:_?\d)*
    )
    (?:[eE][+-]?\d(?:_?\d)*)?
"""

_SI_NUMBER_RE = re.compile(
    rf"""
    ^
    \s*
    (?P<value>{_SI_VALUE_PATTERN})
    \s*
    (?P<prefix>[{_PREFIX_CHARS}]?)
    \s*
    (?P<unit>[A-Za-z]*)?
    \s*
    $
    """,
    re.VERBOSE,
)

_SI_NUMBER_WITH_TRAILING_RE = re.compile(
    rf"""
    ^
    \s*
    (?P<value>{_SI_VALUE_PATTERN})
    \s*
    (?P<prefix>[{_PREFIX_CHARS}])
    \s*
    (?P<trailing>\S.*)
    \s*
    $
    """,
    re.VERBOSE,
)


def _normalize_micro(text: str) -> str:
    return text.replace("μ", "µ")  # U+03BC


def si_parse[T](
    text: str,
    numeric_type: Callable[[Any], T] = float,
) -> T:
    """Parse a string containing an SI-prefixed numeric value.

    Recognised prefixes span quecto (``q``, 10\ :sup:`-30`) through quetta
    (``Q``, 10\ :sup:`30`) including the 2022 additions.  The micro prefix is
    accepted as ``µ`` (U+00B5), ``μ`` (U+03BC), or ASCII ``u``.

    Leading/trailing whitespace and a single optional space between the number
    and its prefix are both accepted.  Underscore separators inside the numeric
    part (PEP 515) are supported.  Any trailing text after a valid
    ``<number><prefix>`` token is silently ignored (e.g. ``"1k/s"`` → ``1000.0``).

    Args:
        text: String to parse, e.g. ``"4.70k"``, ``"2.5 µ"``, ``"1_000M"``.
        numeric_type: Callable applied to the scaled result.  Defaults to
            :class:`float`.  Pass :class:`int`, :class:`~decimal.Decimal`, or
            any other numeric constructor.  :class:`~decimal.Decimal` uses
            exact string-based arithmetic instead of floating-point scaling.

    Returns:
        The parsed value as an instance of *numeric_type*.

    Raises:
        ValueError: If *text* is empty, contains no leading digit, or has
            multiple decimal points.

    Examples:

        >>> si_parse("10k")
        10000.0
        >>> si_parse("500m")
        0.5
        >>> si_parse("1µ")
        1e-06
        >>> si_parse("1 n")
        1e-09
        >>> si_parse("1_000k")
        1000000.0
        >>> si_parse("1R")
        1e+27
        >>> si_parse("4q")
        4e-30
        >>> si_parse("10k", int)
        10000
        >>> from decimal import Decimal
        >>> si_parse("2.5m", Decimal)
        Decimal('0.0025')
    """

    text = _normalize_micro(text.strip())

    match = _SI_NUMBER_RE.match(text)

    if not match:
        match = _SI_NUMBER_WITH_TRAILING_RE.match(text)

    if not match:
        raise ValueError(f"invalid SI value: {text!r}")

    value_text = match.group("value").replace("_", "")
    prefix = match.group("prefix")

    if numeric_type is Decimal:
        value = Decimal(value_text)
        factor = Decimal(str(_SI_FACTORS[prefix]))
        return numeric_type(value * factor)

    scaled = float(value_text) * _SI_FACTORS[prefix]

    return numeric_type(scaled)
