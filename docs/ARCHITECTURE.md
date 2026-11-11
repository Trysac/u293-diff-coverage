# Architecture

This document describes the design and key decisions for `diff-coverage`.

## Core modules

- `parse_diff.py` — parses unified diff hunks and extracts new-side line numbers for added lines.
- `coverage.py` — loads Cobertura XML and coverage.py JSON into a common `Coverage` mapping (`dict[str, dict[int, bool]]`).
- `report.py` — matches diff paths to coverage paths, computes per-file and overall coverage, and builds a frozen `Report`.
- `render.py` — formats a `Report` as plain text or markdown.
- `errors.py` — defines the `DiffCoverageError` exception hierarchy with stable machine-readable codes.
- `__main__.py` — command-line interface.

## Key decisions

### XML safety

We refuse any XML input containing `<!DOCTYPE` or `<!ENTITY` before parsing, which prevents entity expansion attacks. This is a deliberate deviation from many coverage tools that parse XML with external entity processing enabled.

### Path matching

A diff path is matched to a coverage path when they are equal, or one is a suffix of the other after a directory separator. When multiple coverage paths match, the longest one wins; ties raise `ambiguous_path` to force explicit resolution.

### Standard library only

The library intentionally uses only the Python standard library to keep the dependency footprint minimal and avoid supply-chain risks.

## Error handling

All errors derive from `DiffCoverageError` with a stable `code` attribute. Messages are truncated to at most 200 characters and never contain secrets.

## Logging

The package uses `logging.getLogger(__name__)` with a `NullHandler`; no global logging configuration is applied.

## CLI exit codes

| Code | Meaning |
|------|---------|
| 0    | Coverage passed the threshold (or no threshold set) |
| 1    | Coverage below the threshold |
| 2    | Usage, I/O, or parse error |
