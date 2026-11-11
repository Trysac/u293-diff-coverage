"""Error types for the diff_coverage package."""

from __future__ import annotations

from typing import Literal

DiffCoverageErrorCode = Literal[
    "input_too_large",
    "invalid_diff",
    "unsafe_xml",
    "invalid_report",
    "ambiguous_path",
]


class DiffCoverageError(Exception):
    """Base error for diff_coverage.

    Attributes:
        code: Stable machine-readable error code.
    """

    def __init__(self, code: DiffCoverageErrorCode, message: str = "") -> None:
        """Initialize with an error code and an optional human-readable message."""
        self.code: DiffCoverageErrorCode = code
        super().__init__(message[:200])
