# Testing

## Running

```sh
pytest tests/test_diff_coverage.py
```

## Policy

The supplied tests use pytest and exercise the public API. `tests/test_diff_coverage.py` imports `DiffCoverageError`, `diff_coverage`, `load_cobertura`, `load_coverage_json`, `parse_diff`, `render`, and `Decimal`. The cases construct inputs as in-memory strings; no external service or network is required.

## Tiers

The supplied code contains a single pytest module, `tests/test_diff_coverage.py`. No local/CI tier split, conformance marker, or external-tool setup is present in the supplied files.

## Layout

`tests/test_diff_coverage.py` contains the tests. The visible cases cover:

- `parse_diff`: `test_parse_diff_basic`, `test_parse_diff_deleted_file_skipped`, `test_parse_diff_renamed_file`, `test_parse_diff_multiple_hunks`, `test_parse_diff_crlf`, `test_parse_diff_no_newline_marker_ignored`, `test_parse_diff_added_line_starting_with_plus_plus`, `test_parse_diff_removed_line_starting_with_minus_minus`, `test_parse_diff_invalid_hunk`, `test_parse_diff_max_bytes`.
- Cobertura loading: `test_load_cobertura_basic`, `test_load_cobertura_windows_path_and_stripping`, `test_load_cobertura_multiple_classes_any_covered`, `test_load_cobertura_unsafe_xml_doctype`, `test_load_cobertura_unsafe_xml_entity`, `test_load_cobertura_malformed_xml`, `test_load_cobertura_max_bytes`.

No other test files or `tests/conftest.py` appear in the supplied code.
