# diff-coverage

[![PyPI version](https://img.shields.io/pypi/v/trysac-diff-coverage)](https://pypi.org/project/trysac-diff-coverage/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-diff-coverage)](LICENSE)
[![CI](https://github.com/Trysac/u293-diff-coverage/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u293-diff-coverage/actions/workflows/ci.yml)

Measure test coverage of the lines a change adds or modifies by joining a unified diff with Cobertura XML or coverage.py JSON, with safe XML, path matching and a threshold

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-diff-coverage
# or
uv add trysac-diff-coverage
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import diff_coverage

# normalize() trims surrounding whitespace and lower-cases the text.
print(diff_coverage.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    diff_coverage.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
