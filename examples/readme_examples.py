"""Runnable examples mirrored from README.md.

Run from the repository root:
    uv run python examples/readme_examples.py
"""

from decimal import Decimal

from engineering_format import si_format, si_parse


def formatting_basic() -> None:
    print("Formatting: basic")
    print(f"{si_format(4700):.2f}")
    print(format(si_format(1_000_000), ".3f"))
    print(f"{si_format(0.0047):.1f} Ω")
    print()


def formatting_width_alignment() -> None:
    print("Formatting: width and alignment")
    print(f"|{si_format(1000):10.3f}|")
    print(f"|{si_format(1000):<10.3f}|")
    print(f"|{si_format(1000):^10.3f}|")
    print(f"|{si_format(-1000):=+010.3f}|")
    print()


def parsing_basic() -> None:
    print("Parsing")
    print(si_parse("10k"))
    print(si_parse("1_000k"))
    print(si_parse("2.5m", Decimal))
    print(si_parse("1 n"))
    print(si_parse("1k/s"))
    print()


def combined_example() -> None:
    print("Combined")
    value = si_parse("4.7k")
    print(value)
    print(f"{si_format(value):.1f}Ω")
    print(si_parse("2.5m", Decimal))


def main() -> None:
    formatting_basic()
    formatting_width_alignment()
    parsing_basic()
    combined_example()


if __name__ == "__main__":
    main()
