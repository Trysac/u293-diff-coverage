"""Behavior tests for the public API of diff_coverage."""

from __future__ import annotations

import pytest

import diff_coverage


def test_normalize_trims_and_lowercases() -> None:
    assert diff_coverage.normalize("  Hello World ") == "hello world"


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_normalize_rejects_blank_input(value: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        diff_coverage.normalize(value)


def test_version_is_semver() -> None:
    parts = diff_coverage.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
