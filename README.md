# engineering-format

`engineering-format` is a tiny Python library for SI/metric prefix formatting and parsing.

It gives you two public helpers:

- `si_format(value)` wraps a numeric value so it formats with an SI prefix through `format()` or f-strings.
- `si_parse(text, numeric_type=float)` parses an SI-prefixed string back into a number.

The library is intentionally narrow in scope: it handles prefixes, not full unit systems. Append units outside the formatted expression when you need them.

## Installation

Install from PyPI with `uv`:

```bash
uv add engineering-format
```

or:

```bash
uv pip install engineering-format
```

Install from a source checkout with `uv`:

```bash
uv sync
```

If you want to use it in another project from a checkout, install it in editable mode:

```bash
uv pip install -e .
```

## Run All Examples

This repository includes a runnable examples script that mirrors the README code samples:

```bash
uv run python examples/readme_examples.py
```

## Usage

### Formatting

Wrap a value with `si_format()` and pass it to `format()` or an f-string:

```python
from engineering_format import si_format

print(f"{si_format(4700):.2f}")
print(format(si_format(1_000_000), ".3f"))
print(f"{si_format(0.0047):.1f} Ω")
```

Output:

```text
4.70k
1.000M
4.7m Ω
```

Formatting follows Python’s standard float-style format mini-language. Supported presentation types are the float-oriented ones: empty, `e`, `E`, `f`, `F`, `g`, `G`, `n`, and `%`.

For values without an SI prefix, pass `no_prefix_symbol` to provide a suffix
symbol. A space reserves the suffix column when aligning prefixed and
unprefixed values:

Examples:

```python
from engineering_format import si_format

print(f"|{si_format(1000):10.3f}|")
print(f"|{si_format(1000):<10.3f}|")
print(f"|{si_format(1000):^10.3f}|")
print(f"|{si_format(1, no_prefix_symbol=' '):10.3f}|")
print(f"|{si_format(-1000):=+010.3f}|")
```

Output:

```text
|    1.000k|
|1.000k    |
|  1.000k  |
|    1.000 |
|-00001.000k|
```

### Parsing

Parse strings with `si_parse()`:

```python
from decimal import Decimal

from engineering_format import si_parse

print(si_parse("10k"))
print(si_parse("1_000k"))
print(si_parse("2.5m", Decimal))
print(si_parse("1 n"))
print(si_parse("1k/s"))
```

Output:

```text
10000.0
1000000.0
0.0025
1e-09
1000.0
```

Parsing accepts:

- SI prefixes from quecto `q` through quetta `Q`.
- Micro in any of these forms: `µ`, `μ`, or `u`.
- Leading and trailing whitespace.
- An optional space between the number and prefix.
- Underscores in numeric literals.
- Trailing text after a valid `<number><prefix>` token.

When `numeric_type` is `Decimal`, parsing uses exact decimal arithmetic.

## Supported Behavior

`engineering-format` is designed for compact engineering notation, not a general unit library.

What it does well:

- Chooses an SI prefix automatically for formatted numbers.
- Preserves normal Python formatting behavior for width, alignment, sign, grouping, and precision.
- Parses common SI-prefixed strings back into numeric values.

What it does not do:

- It does not attach or interpret units.
- It does not validate that trailing text is a real unit.
- It does not aim to parse arbitrary scientific notation formats beyond the supported numeric forms.

## Examples

```python
from decimal import Decimal

from engineering_format import si_format, si_parse

value = si_parse("4.7k")
print(value)
print(f"{si_format(value):.1f}Ω")
print(si_parse("2.5m", Decimal))
```

Output:

```text
4700.0
4.7kΩ
0.0025
```

## Contributing

Changes should come with tests when they affect formatting or parsing behavior.

CI runs on Python 3.12, 3.13, and 3.14 for every pull request and for pushes to main/master, and enforces both Ruff and pytest.

Run the checks before opening a pull request:

```bash
uv run pytest
uv run ruff check .
```

If you change documented behavior, update the examples in this README at the same time. The README is the main user-facing documentation for this project.

## License

MIT License

Copyright (c) 2026 Karsten van Zwol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
