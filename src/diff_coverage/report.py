"""Compute diff coverage reports from changed lines and coverage data."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from .coverage import Coverage
from .errors import DiffCoverageError


@dataclass(frozen=True)
class FileReport:
    """Coverage summary for a single changed file."""

    path: str
    covered: int
    executable: int
    missing: list[int]


@dataclass(frozen=True)
class Report:
    """Overall diff coverage report."""

    files: list[FileReport]
    percent: Decimal | None
    passed: bool
    unmeasured_files: list[str]


def _match_coverage_path(diff_path: str, coverage_paths: list[str]) -> str:
    """Return the best matching coverage path for a diff path.

    Matching rules:
    - Equal strings match.
    - diff_path ends with '/' + coverage_path.
    - coverage_path ends with '/' + diff_path.
    Among matches, the longest coverage_path wins; a tie raises
    ``DiffCoverageError('ambiguous_path')``.
    """
    matches: list[str] = []
    for cov_path in coverage_paths:
        if (
            diff_path == cov_path
            or diff_path.endswith("/" + cov_path)
            or cov_path.endswith("/" + diff_path)
        ):
            matches.append(cov_path)

    if not matches:
        return ""

    max_len = max(len(p) for p in matches)
    best = [p for p in matches if len(p) == max_len]
    if len(best) > 1 and len(set(best)) > 1:
        raise DiffCoverageError(
            "ambiguous_path",
            f"multiple coverage paths match {diff_path!r}: {', '.join(best[:5])}",
        )
    return best[0]


def diff_coverage(
    changed: Mapping[str, set[int]],
    coverage: Coverage,
    *,
    fail_under: Decimal | None = None,
) -> Report:
    """Compute coverage of changed executable lines.

    Args:
        changed: Mapping from diff path to set of new-side line numbers.
        coverage: Coverage mapping as returned by :func:`load_cobertura` or
            :func:`load_coverage_json`.
        fail_under: Optional minimum percentage threshold. If given, ``passed``
            is ``percent >= fail_under``; if ``percent`` is ``None`` (no
            executable changed lines) ``passed`` is always ``True``.

    Returns:
        A frozen Report with per-file details, overall percent, pass status,
        and list of changed files with no matching coverage path.

    Raises:
        DiffCoverageError: If multiple coverage paths match a diff path with
            the same maximum length (ambiguous_path).
    """
    coverage_paths = list(coverage.keys())
    files: list[FileReport] = []
    unmeasured: list[str] = []
    total_covered = 0
    total_executable = 0

    for diff_path in sorted(changed):
        cov_path = _match_coverage_path(diff_path, coverage_paths)
        if not cov_path:
            unmeasured.append(diff_path)
            continue

        line_cover = coverage.get(cov_path, {})
        covered = 0
        executable = 0
        missing: list[int] = []
        for line_no in sorted(changed[diff_path]):
            if line_no in line_cover:
                executable += 1
                if line_cover[line_no]:
                    covered += 1
                else:
                    missing.append(line_no)

        files.append(
            FileReport(
                path=diff_path,
                covered=covered,
                executable=executable,
                missing=missing,
            )
        )
        total_covered += covered
        total_executable += executable

    if total_executable == 0:
        percent = None
        passed = True
    else:
        percent = (Decimal(total_covered) * 100 / Decimal(total_executable)).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )
        passed = True if fail_under is None else percent >= fail_under

    return Report(
        files=files,
        percent=percent,
        passed=passed,
        unmeasured_files=unmeasured,
    )
