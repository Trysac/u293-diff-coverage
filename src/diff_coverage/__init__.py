"""Measure coverage of the lines a change adds or modifies.

The package joins a unified diff with a coverage report (Cobertura XML or
coverage.py JSON) and reports how many of the changed executable lines were
exercised by tests.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from decimal import Decimal
from typing import Literal

from .coverage import Coverage, load_cobertura, load_coverage_json
from .errors import DiffCoverageError, DiffCoverageErrorCode
from .parse_diff import parse_diff
from .render import render
from .report import FileReport, Report, diff_coverage

__all__ = [
    "Coverage",
    "Decimal",
    "DiffCoverageError",
    "DiffCoverageErrorCode",
    "FileReport",
    "Literal",
    "Mapping",
    "Report",
    "diff_coverage",
    "load_cobertura",
    "load_coverage_json",
    "parse_diff",
    "render",
]

__version__ = "0.1.0"

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
