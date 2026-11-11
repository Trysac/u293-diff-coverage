"""Command-line interface for diff_coverage."""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal, InvalidOperation

from .coverage import load_cobertura, load_coverage_json
from .errors import DiffCoverageError
from .parse_diff import parse_diff
from .render import render
from .report import diff_coverage


def _percent(text: str) -> Decimal:
    """Parse a percentage argument, raising an argparse type error when invalid."""
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"invalid percentage: {text!r}") from exc
    if not value.is_finite():
        raise argparse.ArgumentTypeError("percentage must be finite")
    return value


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code.

    Exit codes:
        0: coverage passed the threshold (or no threshold set).
        1: coverage below the threshold.
        2: usage error, file I/O error, or parse error.
    """
    parser = argparse.ArgumentParser(
        prog="diff_coverage",
        description="Measure coverage of the lines changed by a diff.",
    )
    parser.add_argument("--diff", required=True, help="Path to unified diff file")
    parser.add_argument(
        "--coverage", required=True, help="Path to Cobertura XML or coverage.py JSON file"
    )
    parser.add_argument(
        "--fail-under",
        type=_percent,
        default=None,
        help="Minimum coverage percentage (e.g. 80)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args(argv)

    try:
        with open(args.diff, encoding="utf-8-sig") as f:
            diff_text = f.read()
        changed = parse_diff(diff_text)

        with open(args.coverage, encoding="utf-8-sig") as f:
            coverage_text = f.read()
        stripped = coverage_text.lstrip()
        if stripped.startswith("<"):
            coverage = load_cobertura(coverage_text)
        elif stripped.startswith("{"):
            coverage = load_coverage_json(coverage_text)
        else:
            print(
                "Cannot determine coverage format; expected XML (<) or JSON ({)",
                file=sys.stderr,
            )
            return 2

        report = diff_coverage(changed, coverage, fail_under=args.fail_under)
    except (OSError, UnicodeError, DiffCoverageError, InvalidOperation) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(render(report, args.format))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
