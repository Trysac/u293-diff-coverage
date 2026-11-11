# Use standard library and safe XML for diff coverage measurement

Status: accepted (generated, pending human review)

## Context

The utility must join unified diffs with Cobertura XML or coverage.py JSON to compute coverage of changed lines. XML reports are untrusted and may contain entity expansion attacks.

## Decision

Implement the entire feature with Python standard library modules. Refuse XML inputs containing DOCTYPE or ENTITY before parsing to block XXE. Define a stable DiffCoverageError with machine-readable codes and explicit path matching rules.

## Consequences

The library has no runtime dependencies, improving supply-chain safety. XML parsing is safe against common attacks. Ambiguous path matches raise an error to avoid silently picking an incorrect report. The API is pure and side-effect free, suitable for embedding in other tools.
