"""Render a Report as text or markdown."""

from __future__ import annotations

from typing import Literal

from .report import Report


def _format_missing(missing: list[int]) -> str:
    """Format a sorted list of integers as ranges like '3-5, 9'."""
    if not missing:
        return ""
    ranges: list[str] = []
    start = prev = missing[0]
    for num in missing[1:]:
        if num == prev + 1:
            prev = num
        else:
            if start == prev:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
            start = prev = num
    if start == prev:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{prev}")
    return ", ".join(ranges)


def render(report: Report, fmt: Literal["text", "markdown"]) -> str:
    """Render a coverage Report.

    Args:
        report: The Report to render.
        fmt: Output format; either ``'text'`` or ``'markdown'``.

    Returns:
        The rendered string.
    """
    if fmt == "text":
        lines = []
        for file in report.files:
            missing_str = _format_missing(file.missing)
            if missing_str:
                lines.append(f"{file.path} {file.covered}/{file.executable} missing {missing_str}")
            else:
                lines.append(f"{file.path} {file.covered}/{file.executable}")
        if report.percent is None:
            lines.append("Diff coverage: no executable changed lines")
        else:
            lines.append(f"Diff coverage: {report.percent}%")
        return "\n".join(lines)

    if fmt == "markdown":
        if report.percent is None:
            heading = "## Diff coverage: no executable changed lines"
        else:
            heading = f"## Diff coverage: {report.percent}%"
        lines = [heading, "", "| File | Covered | Missing lines |", "| --- | --- | --- |"]
        for file in report.files:
            missing_str = _format_missing(file.missing)
            lines.append(f"| {file.path} | {file.covered}/{file.executable} | {missing_str} |")
        return "\n".join(lines) + "\n"

    raise ValueError(f"unsupported format: {fmt}")
