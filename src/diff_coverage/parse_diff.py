"""Parse unified diff hunks into changed new-side line numbers."""

from __future__ import annotations

import re

from .errors import DiffCoverageError

_HUNK_RE = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? "
    r"\+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)


def parse_diff(text: str, *, max_bytes: int = 10_485_760) -> dict[str, set[int]]:
    """Extract new-side line numbers for each added line from a unified diff.

    Args:
        text: The diff text, with or without CRLF line endings.
        max_bytes: Maximum allowed size of the diff text in UTF-8 bytes.

    Returns:
        Mapping from new file path (with ``a/`` and ``b/`` prefixes stripped)
        to a set of new-side line numbers where lines were added.

    Raises:
        DiffCoverageError: If the input exceeds ``max_bytes`` or a hunk header
            is malformed (code ``input_too_large`` or ``invalid_diff``).
    """
    if len(text.encode("utf-8")) > max_bytes:
        raise DiffCoverageError("input_too_large", "diff input exceeds maximum size")

    result: dict[str, set[int]] = {}
    current_path: str | None = None
    skip_current = False
    # ``new_line`` is not None only while inside a hunk body.
    new_line: int | None = None
    old_remaining = 0
    new_remaining = 0

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\r")

        if new_line is not None:
            # Inside a hunk the line prefixes are authoritative: an added line
            # whose content starts with "++ " shows up here as "+++ ...", so it
            # must not be mistaken for a file header.
            handled = True
            if line.startswith("\\"):
                # '\ No newline at end of file' marker; ignore.
                pass
            elif line.startswith("+"):
                if current_path is not None and not skip_current:
                    result[current_path].add(new_line)
                new_line += 1
                new_remaining -= 1
            elif line.startswith("-"):
                old_remaining -= 1
            elif line.startswith(" ") or line == "":
                # Context line (an empty line is a context line with stripped
                # trailing whitespace); consumes a line on both sides.
                new_line += 1
                new_remaining -= 1
                old_remaining -= 1
            else:
                # Not a hunk body line; leave the hunk and re-examine it.
                handled = False

            if handled:
                if new_remaining <= 0 and old_remaining <= 0:
                    new_line = None
                continue
            new_line = None

        if line.startswith("+++ "):
            # New file path.
            path = line[4:].strip()
            # Strip a/ or b/ prefixes if present.
            if path.startswith("b/") or path.startswith("a/"):
                path = path[2:]
            if path == "/dev/null":
                current_path = None
                skip_current = True
            else:
                current_path = path
                skip_current = False
                result.setdefault(current_path, set())
            new_line = None
            continue

        if line.startswith("@@ "):
            match = _HUNK_RE.match(line)
            if not match:
                raise DiffCoverageError("invalid_diff", f"invalid hunk header: {line[:80]}")
            old_remaining = int(match.group("old_count") or 1)
            new_remaining = int(match.group("new_count") or 1)
            new_line = int(match.group("new_start"))
            if new_remaining <= 0 and old_remaining <= 0:
                new_line = None
            continue

    return result
