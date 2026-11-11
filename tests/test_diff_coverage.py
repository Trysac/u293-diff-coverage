"""Tests for diff_coverage public API and CLI."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from diff_coverage import (
    DiffCoverageError,
    diff_coverage,
    load_cobertura,
    load_coverage_json,
    parse_diff,
    render,
)


def test_parse_diff_basic() -> None:
    diff = "diff --git a/src/m.py b/src/m.py\n--- a/src/m.py\n+++ b/src/m.py\n@@ -1,3 +1,4 @@\n a\n-b\n+B\n+C\n c\n"
    assert parse_diff(diff) == {"src/m.py": {2, 3}}


def test_parse_diff_deleted_file_skipped() -> None:
    diff = (
        "diff --git a/old.py b/old.py\n"
        "--- a/old.py\n"
        "+++ /dev/null\n"
        "@@ -1,2 +0,0 @@\n"
        "-line1\n"
        "-line2\n"
    )
    assert parse_diff(diff) == {}


def test_parse_diff_renamed_file() -> None:
    diff = (
        "diff --git a/old.py b/new.py\n"
        "similarity index 90%\n"
        "rename from old.py\n"
        "rename to new.py\n"
        "--- a/old.py\n"
        "+++ b/new.py\n"
        "@@ -1,1 +1,2 @@\n"
        "-old\n"
        "+new\n"
        "+extra\n"
    )
    result = parse_diff(diff)
    assert "old.py" not in result
    assert result == {"new.py": {1, 2}}


def test_parse_diff_multiple_hunks() -> None:
    diff = (
        "diff --git a/file.py b/file.py\n"
        "--- a/file.py\n"
        "+++ b/file.py\n"
        "@@ -1,1 +1,2 @@\n"
        " context\n"
        "+added1\n"
        "@@ -10,0 +11,3 @@\n"
        "+added2\n"
        "+added3\n"
        "+added4\n"
    )
    assert parse_diff(diff) == {"file.py": {2, 11, 12, 13}}


def test_parse_diff_crlf() -> None:
    diff = "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1,1 +1,1 @@\n-old\r\n+new\r\n"
    assert parse_diff(diff) == {"x.py": {1}}


def test_parse_diff_no_newline_marker_ignored() -> None:
    diff = (
        "diff --git a/x.py b/x.py\n"
        "--- a/x.py\n"
        "+++ b/x.py\n"
        "@@ -1,1 +1,2 @@\n"
        "-old\n"
        "\\ No newline at end of file\n"
        "+new\n"
        "+more\n"
    )
    assert parse_diff(diff) == {"x.py": {1, 2}}


def test_parse_diff_added_line_starting_with_plus_plus() -> None:
    # An added line whose content is "++ note" appears as "+++ note" and must
    # not be mistaken for a file header.
    diff = "diff --git a/n.md b/n.md\n--- a/n.md\n+++ b/n.md\n@@ -1,2 +1,3 @@\n a\n+++ note\n b\n"
    assert parse_diff(diff) == {"n.md": {2}}


def test_parse_diff_removed_line_starting_with_minus_minus() -> None:
    # A removed line whose content is "-- note" appears as "--- note".
    diff = (
        "diff --git a/n.md b/n.md\n"
        "--- a/n.md\n"
        "+++ b/n.md\n"
        "@@ -1,3 +1,3 @@\n"
        " a\n"
        "--- note\n"
        "+replacement\n"
        " b\n"
    )
    assert parse_diff(diff) == {"n.md": {2}}


def test_parse_diff_invalid_hunk() -> None:
    diff = "@@ -1 +x @@\n"
    with pytest.raises(DiffCoverageError) as excinfo:
        parse_diff(diff)
    assert excinfo.value.code == "invalid_diff"


def test_parse_diff_max_bytes() -> None:
    with pytest.raises(DiffCoverageError) as excinfo:
        parse_diff("x" * 10_485_761, max_bytes=10_485_760)
    assert excinfo.value.code == "input_too_large"


def test_load_cobertura_basic() -> None:
    xml = (
        "<coverage><sources><source>/repo</source></sources>"
        "<packages><package><classes>"
        '<class filename="src/m.py">'
        "<lines>"
        '<line number="2" hits="1"/>'
        '<line number="3" hits="0"/>'
        "</lines>"
        "</class>"
        "</classes></package></packages></coverage>"
    )
    cov = load_cobertura(xml)
    assert cov == {"src/m.py": {2: True, 3: False}}


def test_load_cobertura_windows_path_and_stripping() -> None:
    xml = (
        "<coverage>"
        "<packages><package><classes>"
        '<class filename=".\\src\\m.py">'
        '<lines><line number="2" hits="1"/></lines>'
        "</class>"
        "</classes></package></packages></coverage>"
    )
    cov = load_cobertura(xml)
    assert cov == {"src/m.py": {2: True}}


def test_load_cobertura_multiple_classes_any_covered() -> None:
    xml = (
        "<coverage><packages><package><classes>"
        '<class filename="a.py">'
        '<lines><line number="10" hits="0"/></lines>'
        "</class>"
        '<class filename="a.py">'
        '<lines><line number="10" hits="2"/></lines>'
        "</class>"
        "</classes></package></packages></coverage>"
    )
    cov = load_cobertura(xml)
    assert cov == {"a.py": {10: True}}


def test_load_cobertura_unsafe_xml_doctype() -> None:
    xml = "<!DOCTYPE foo><coverage/>"
    with pytest.raises(DiffCoverageError) as excinfo:
        load_cobertura(xml)
    assert excinfo.value.code == "unsafe_xml"


def test_load_cobertura_unsafe_xml_entity() -> None:
    xml = "<!ENTITY x SYSTEM 'file:///etc/passwd'><coverage/>"
    with pytest.raises(DiffCoverageError) as excinfo:
        load_cobertura(xml)
    assert excinfo.value.code == "unsafe_xml"


def test_load_cobertura_malformed_xml() -> None:
    xml = "<coverage><unclosed>"
    with pytest.raises(DiffCoverageError) as excinfo:
        load_cobertura(xml)
    assert excinfo.value.code == "invalid_report"


def test_load_cobertura_max_bytes() -> None:
    with pytest.raises(DiffCoverageError) as excinfo:
        load_cobertura("x" * 52_428_801, max_bytes=52_428_800)
    assert excinfo.value.code == "input_too_large"


def test_load_coverage_json_basic_and_equal_to_cobertura() -> None:
    json_text = '{"files": {"src/m.py": {"executed_lines": [2], "missing_lines": [3]}}}'
    cov = load_coverage_json(json_text)
    assert cov == {"src/m.py": {2: True, 3: False}}

    # Compare with Cobertura result for same data (should match)
    xml = (
        "<coverage><packages><package><classes>"
        '<class filename="src/m.py">'
        '<lines><line number="2" hits="1"/><line number="3" hits="0"/></lines>'
        "</class>"
        "</classes></package></packages></coverage>"
    )
    cov_xml = load_cobertura(xml)
    assert cov == cov_xml


def test_load_coverage_json_invalid() -> None:
    with pytest.raises(DiffCoverageError) as excinfo:
        load_coverage_json("not json")
    assert excinfo.value.code == "invalid_report"


def test_diff_coverage_full_scenario_unmeasured_file() -> None:
    changed = {
        "src/m.py": {2, 3, 4},  # line 4 absent from coverage
        "docs/x.md": {1},
    }
    coverage = {
        "src/m.py": {2: True, 3: False},
    }
    report = diff_coverage(changed, coverage)
    assert report.percent == Decimal("50.0")
    assert report.passed is True
    assert report.unmeasured_files == ["docs/x.md"]
    assert len(report.files) == 1
    file_report = report.files[0]
    assert file_report.path == "src/m.py"
    assert file_report.covered == 1
    assert file_report.executable == 2
    assert file_report.missing == [3]


def test_diff_coverage_percent_and_threshold() -> None:
    changed = {"a.py": {1, 2, 3}}
    coverage = {"a.py": {1: True, 2: True, 3: False}}
    report = diff_coverage(changed, coverage)
    assert report.percent == Decimal("66.7")
    assert report.passed

    report_fail = diff_coverage(changed, coverage, fail_under=Decimal("80"))
    assert report_fail.passed is False

    report_pass = diff_coverage(changed, coverage, fail_under=Decimal("66.7"))
    assert report_pass.passed is True


def test_diff_coverage_no_executable() -> None:
    changed = {"a.py": {1, 2}}
    coverage = {"a.py": {}}
    report = diff_coverage(changed, coverage)
    assert report.percent is None
    assert report.passed is True
    assert len(report.files) == 1
    assert report.files[0].executable == 0
    assert report.files[0].covered == 0
    assert report.files[0].missing == []


def test_path_matching_and_ambiguous() -> None:
    changed = {"src/m.py": {1}}
    coverage = {
        "m.py": {1: True},
        "src/m.py": {1: False},
    }
    report = diff_coverage(changed, coverage)
    # Longest match src/m.py should win
    assert report.files[0].covered == 0
    assert report.files[0].executable == 1
    assert report.files[0].missing == [1]

    # Tie -> ambiguous
    changed = {"m.py": {1}}
    coverage = {
        "a/m.py": {1: True},
        "b/m.py": {1: False},
    }
    with pytest.raises(DiffCoverageError) as excinfo:
        diff_coverage(changed, coverage)
    assert excinfo.value.code == "ambiguous_path"


def test_render_text() -> None:
    report = diff_coverage(
        {"src/m.py": {2, 3}},
        {"src/m.py": {2: True, 3: False}},
    )
    text = render(report, "text")
    assert text == "src/m.py 1/2 missing 3\nDiff coverage: 50.0%"


def test_render_text_no_missing() -> None:
    report = diff_coverage(
        {"a.py": {1}},
        {"a.py": {1: True}},
    )
    text = render(report, "text")
    assert text == "a.py 1/1\nDiff coverage: 100.0%"


def test_render_text_no_executable() -> None:
    report = diff_coverage(
        {"a.py": {1}},
        {"a.py": {}},
    )
    text = render(report, "text")
    assert text == "a.py 0/0\nDiff coverage: no executable changed lines"


def test_render_markdown_exact_acceptance() -> None:
    report = diff_coverage(
        {"src/m.py": {2, 3}},
        {"src/m.py": {2: True, 3: False}},
    )
    md = render(report, "markdown")
    assert (
        md
        == "## Diff coverage: 50.0%\n\n| File | Covered | Missing lines |\n| --- | --- | --- |\n| src/m.py | 1/2 | 3 |\n"
    )


def test_format_missing_ranges() -> None:
    from diff_coverage.render import _format_missing

    assert _format_missing([3, 4, 5, 9]) == "3-5, 9"
    assert _format_missing([1]) == "1"
    assert _format_missing([]) == ""


def test_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from diff_coverage.__main__ import main

    diff_file = tmp_path / "d.patch"
    diff_file.write_text(
        "diff --git a/src/m.py b/src/m.py\n"
        "--- a/src/m.py\n"
        "+++ b/src/m.py\n"
        "@@ -1,1 +1,3 @@\n"
        " a\n"
        "+new\n"
        "+untested\n",
        encoding="utf-8",
    )
    coverage_file = tmp_path / "coverage.xml"
    coverage_file.write_text(
        "<coverage><packages><package><classes>"
        '<class filename="src/m.py">'
        "<lines>"
        '<line number="2" hits="1"/>'
        '<line number="3" hits="0"/>'
        "</lines>"
        "</class>"
        "</classes></package></packages></coverage>",
        encoding="utf-8",
    )
    exit_code = main(
        ["--diff", str(diff_file), "--coverage", str(coverage_file), "--fail-under", "80"],
    )
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "src/m.py 1/2 missing 3" in captured.out
    assert "Diff coverage: 50.0%" in captured.out

    exit_code_pass = main(
        ["--diff", str(diff_file), "--coverage", str(coverage_file), "--fail-under", "50"],
    )
    captured_pass = capsys.readouterr()
    assert exit_code_pass == 0
    assert "Diff coverage: 50.0%" in captured_pass.out

    missing = tmp_path / "missing.patch"
    exit_code_missing = main(["--diff", str(missing), "--coverage", str(coverage_file)])
    captured_missing = capsys.readouterr()
    assert exit_code_missing == 2
    assert "Error:" in captured_missing.err


def test_cli_format_markdown(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from diff_coverage.__main__ import main

    diff_file = tmp_path / "d.patch"
    diff_file.write_text(
        "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1,1 +1,1 @@\n-old\n+new\n",
        encoding="utf-8",
    )
    cov_file = tmp_path / "cov.json"
    cov_file.write_text(
        '{"files": {"a.py": {"executed_lines": [1], "missing_lines": []}}}',
        encoding="utf-8",
    )
    exit_code = main(
        ["--diff", str(diff_file), "--coverage", str(cov_file), "--format", "markdown"],
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.startswith("## Diff coverage: 100.0%\n\n")
    assert "| a.py | 1/1 |  |" in captured.out


def _write_cli_inputs(tmp_path: Path) -> tuple[Path, Path]:
    diff_file = tmp_path / "d.patch"
    diff_file.write_text(
        "diff --git a/src/m.py b/src/m.py\n"
        "--- a/src/m.py\n"
        "+++ b/src/m.py\n"
        "@@ -1,1 +1,2 @@\n"
        " a\n"
        "+new\n",
        encoding="utf-8",
    )
    coverage_file = tmp_path / "coverage.xml"
    coverage_file.write_text(
        "<coverage><packages><package><classes>"
        '<class filename="src/m.py">'
        "<lines>"
        '<line number="2" hits="1"/>'
        "</lines>"
        "</class>"
        "</classes></package></packages></coverage>",
        encoding="utf-8",
    )
    return diff_file, coverage_file


def test_cli_invalid_fail_under_is_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from diff_coverage.__main__ import main

    diff_file, coverage_file = _write_cli_inputs(tmp_path)
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "--diff",
                str(diff_file),
                "--coverage",
                str(coverage_file),
                "--fail-under",
                "abc",
            ]
        )
    assert excinfo.value.code == 2


def test_cli_latin1_coverage_is_io_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from diff_coverage.__main__ import main

    diff_file, _ = _write_cli_inputs(tmp_path)
    coverage_file = tmp_path / "latin1.xml"
    xml = (
        "<coverage><!-- caf\u00e9 --><packages><package><classes>"
        '<class filename="src/m.py">'
        '<lines><line number="2" hits="1"/></lines>'
        "</class>"
        "</classes></package></packages></coverage>"
    )
    coverage_file.write_bytes(xml.encode("latin-1"))

    exit_code = main(["--diff", str(diff_file), "--coverage", str(coverage_file)])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Error:" in captured.err


def test_cli_utf8_bom_coverage(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from diff_coverage.__main__ import main

    diff_file, _ = _write_cli_inputs(tmp_path)
    coverage_file = tmp_path / "bom.xml"
    coverage_file.write_text(
        "<coverage><packages><package><classes>"
        '<class filename="src/m.py">'
        '<lines><line number="2" hits="1"/></lines>'
        "</class>"
        "</classes></package></packages></coverage>",
        encoding="utf-8-sig",
    )

    exit_code = main(["--diff", str(diff_file), "--coverage", str(coverage_file)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Diff coverage: 100.0%" in captured.out
