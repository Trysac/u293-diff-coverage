# Security

This document describes the security considerations for `diff-coverage`.

## Threat model

### Defended

- XML entity expansion / XXE: `load_cobertura` rejects any input whose lowercased text contains `<!doctype` or `<!entity` with `DiffCoverageError('unsafe_xml')` before calling `xml.etree.ElementTree.XML`.
- Oversized inputs: `parse_diff` rejects text larger than `10_485_760` UTF-8 bytes; `load_cobertura` and `load_coverage_json` reject text larger than `52_428_800` UTF-8 bytes. These raise `DiffCoverageError('input_too_large')`.
- Malformed Cobertura XML raises `DiffCoverageError('invalid_report')`; malformed coverage JSON raises `DiffCoverageError('invalid_report')`.
- Overlong exception messages: `DiffCoverageError.__init__` stores `super().__init__(message[:200])`.

### Not defended

- Path matching is string suffix matching; the library does not resolve, canonicalize, or sandbox filesystem paths. The CLI opens the file paths supplied on the command line.
- The byte caps bound total input size only. The code imposes no separate limits on the number of files, lines, or hunk entries within that size.
- Error messages are not guaranteed to be secret-free: invalid hunk headers include up to 80 characters of the header, ambiguous-path errors include up to five matching coverage paths, and XML parse errors include the parser message.
- Branch coverage, running git, LCOV and JaCoCo parsing, and comment posting are out of scope.

## XML parsing

The library refuses any XML input containing `<!DOCTYPE` or `<!ENTITY` (case-insensitive) before parsing. This prevents classic XML External Entity (XXE) and entity expansion attacks. Malformed XML raises `DiffCoverageError` with code `invalid_report`.

## Input size limits

All text inputs enforce a maximum byte size: `10_485_760` for diffs and `52_428_800` for coverage reports. Inputs beyond the limit raise `input_too_large`.

## Error messages

Error messages are truncated to at most 200 characters. Some messages contain input fragments as listed under the threat model.
