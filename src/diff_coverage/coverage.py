"""Load coverage data from Cobertura XML and coverage.py JSON."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET

from .errors import DiffCoverageError

Coverage = dict[str, dict[int, bool]]


def _check_size(text: str, max_bytes: int) -> None:
    if len(text.encode("utf-8")) > max_bytes:
        raise DiffCoverageError("input_too_large", "coverage input exceeds maximum size")


def _parse_int(value: str | None) -> int | None:
    """Parse an XML integer attribute, returning ``None`` when missing or invalid."""
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _normalize_filename(filename: str) -> str:
    """Normalise a Cobertura class filename to a portable path.

    Replaces Windows backslashes with forward slashes and strips leading
    ``./`` sequences.
    """
    path = filename.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def load_cobertura(text: str, *, max_bytes: int = 52_428_800) -> Coverage:
    """Parse a Cobertura XML report into a Coverage mapping.

    Args:
        text: Cobertura XML document.
        max_bytes: Maximum allowed size in UTF-8 bytes.

    Returns:
        Mapping from normalized file path to a dict of line number to covered
        boolean. A line covered by any class entry is True.

    Raises:
        DiffCoverageError: If the input is too large, contains an XML DOCTYPE
            or ENTITY (unsafe), or is malformed XML (invalid_report).
    """
    _check_size(text, max_bytes)
    lowered = text.lower()
    if "<!doctype" in lowered or "<!entity" in lowered:
        raise DiffCoverageError("unsafe_xml", "XML input contains DOCTYPE or ENTITY")

    try:
        root = ET.XML(text)
    except ET.ParseError as exc:
        raise DiffCoverageError("invalid_report", f"malformed XML: {exc}") from exc

    coverage: Coverage = {}
    for class_elem in root.iter("class"):
        filename = class_elem.get("filename")
        if filename is None:
            continue
        path = _normalize_filename(filename)
        line_map = coverage.setdefault(path, {})
        for line_elem in class_elem.findall("lines/line"):
            line_no = _parse_int(line_elem.get("number"))
            hits = _parse_int(line_elem.get("hits"))
            if line_no is None or hits is None:
                continue
            covered = hits > 0
            # If line already exists, keep True if any entry covered it.
            if line_no not in line_map or not line_map[line_no]:
                line_map[line_no] = covered
    return coverage


def load_coverage_json(text: str, *, max_bytes: int = 52_428_800) -> Coverage:
    """Parse a coverage.py JSON report into a Coverage mapping.

    Args:
        text: JSON report as produced by ``coverage json``.
        max_bytes: Maximum allowed size in UTF-8 bytes.

    Returns:
        Mapping from file path to a dict of line number to covered boolean.

    Raises:
        DiffCoverageError: If the input is too large or not valid JSON.
    """
    _check_size(text, max_bytes)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DiffCoverageError("invalid_report", f"invalid JSON: {exc}") from exc

    if not isinstance(data, dict) or "files" not in data:
        raise DiffCoverageError("invalid_report", "missing 'files' key in coverage JSON")

    files = data["files"]
    if not isinstance(files, dict):
        raise DiffCoverageError("invalid_report", "'files' must be an object")

    coverage: Coverage = {}
    for path, file_info in files.items():
        if not isinstance(file_info, dict):
            continue
        executed = file_info.get("executed_lines", [])
        missing = file_info.get("missing_lines", [])
        if not isinstance(executed, list) or not isinstance(missing, list):
            continue
        line_map = coverage.setdefault(path, {})
        for line_no in executed:
            if isinstance(line_no, int):
                line_map[line_no] = True
        for line_no in missing:
            if isinstance(line_no, int):
                line_map[line_no] = False
    return coverage
