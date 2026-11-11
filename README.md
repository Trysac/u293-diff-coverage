# diff-coverage

Measure test coverage of exactly the lines a change adds or modifies by joining a unified diff with a Cobertura XML or coverage.py JSON report.

[![PyPI version](https://img.shields.io/pypi/v/trysac-diff-coverage)](https://pypi.org/project/trysac-diff-coverage/)
[![Python versions](https://img.shields.io/pypi/pyversions/trysac-diff-coverage)](https://pypi.org/project/trysac-diff-coverage/)

## Features

- Standard library only; no runtime dependencies.
- Safe XML parsing: `load_cobertura` refuses inputs containing `<!DOCTYPE` or `<!ENTITY` (case-insensitive) before parsing, blocking entity expansion attacks.
- Explicit path matching between diff paths and coverage report paths; the longest matching coverage path wins and a tie raises `DiffCoverageError('ambiguous_path')`.
- Computes the percentage as `Decimal`, quantized to `0.1` with `ROUND_HALF_UP`, and enforces an optional `fail_under` threshold.
- Renders text or markdown summaries and condenses missing line numbers into ranges such as `3-5, 9`.
- Command-line interface in `diff_coverage.__main__` for CI integration.

## Installation

```bash
pip install trysac-diff-coverage
```

The import name is `diff_coverage`.

## Usage

### Library

```python
from decimal import Decimal
from diff_coverage import parse_diff, load_cobertura, diff_coverage, render

diff_text = "diff --git a/src/m.py b/src/m.py\n--- a/src/m.py\n+++ b/src/m.py\n@@ -1,3 +1,4 @@\n a\n-b\n+B\n+C\n c\n"
xml_text = "<coverage><packages><package><classes><class filename='src/m.py'><lines><line number='2' hits='1'/><line number='3' hits='0'/></lines></class></classes></package></packages></coverage>"
changed = parse_diff(diff_text)
report = diff_coverage(changed, load_cobertura(xml_text), fail_under=Decimal("80"))
print(render(report, "text"))
```

This prints:

```text
src/m.py 1/2 missing 3
Diff coverage: 50.0%
```

### Public API

- `parse_diff(text: str, *, max_bytes: int = 10_485_760) -> dict[str, set[int]]` returns new-side line numbers of added lines per new path. It strips `a/` and `b/` prefixes, skips `+++ /dev/null` files, ignores `\ No newline at end of file`, and tolerates CRLF. It raises `DiffCoverageError` with code `input_too_large` or `invalid_diff`.
- `load_cobertura(text: str, *, max_bytes: int = 52_428_800) -> Coverage` returns `dict[str, dict[int, bool]]`. It normalizes backslashes to `/`, strips leading `./`, and treats a line as covered when any class entry has `hits > 0`. It raises `input_too_large`, `unsafe_xml`, or `invalid_report`.
- `load_coverage_json(text: str, *, max_bytes: int = 52_428_800) -> Coverage` reads `files.<path>.executed_lines` and `missing_lines`. It raises `input_too_large` or `invalid_report`.
- `diff_coverage(changed, coverage, *, fail_under: Decimal | None = None) -> Report` returns frozen `Report(files, percent, passed, unmeasured_files)`, where each `FileReport` has `path`, `covered`, `executable`, and `missing`. It raises `DiffCoverageError('ambiguous_path')` on a longest-match tie.
- `render(report, fmt: Literal['text','markdown']) -> str` returns text or markdown; any other format raises `ValueError`.

`DiffCoverageError.code` is one of `input_too_large`, `invalid_diff`, `unsafe_xml`, `invalid_report`, `ambiguous_path`. Messages are truncated to at most 200 characters. `fail_under` applies only when `percent` is not `None`; with no executable changed lines `percent` is `None` and `passed` is `True`.

### Command line

```bash
python -m diff_coverage --diff change.patch --coverage coverage.xml --fail-under 80 --format text
```

The coverage format is detected from the first non-whitespace character: `<` for Cobertura XML, `{` for coverage.py JSON. Other content returns exit code `2`. Exit codes: `0` passed or no threshold, `1` below threshold, `2` usage, I/O, or parse error.

## Why not diff-cover

`diff-cover` is the best-known alternative. This utility uses only the Python standard library, refuses XML containing `<!DOCTYPE` or `<!ENTITY` before parsing, and defines explicit path matching rules with a pure API for other tools. It does not run git, read LCOV or JaCoCo, compute branch coverage, or post comments.

## Documentation

- [Security](docs/SECURITY.md)
- [Project](docs/PROJECT.md)
- [Testing](docs/TESTING.md)

## License

MIT
