# Project record

## Objective

Measure test coverage of the lines a change adds or modifies by joining a unified diff with Cobertura XML or coverage.py JSON, with safe XML, path matching and a threshold.

## Scope

In scope: parsing unified diff hunks, loading Cobertura XML and coverage.py JSON into a common `Coverage` mapping, matching diff paths to coverage paths, computing per-file and overall diff coverage, enforcing an optional `fail_under` threshold, rendering text or markdown, and a command-line interface. The implementation uses the Python standard library only.

Out of scope: branch coverage, running git, LCOV and JaCoCo formats, and comment posting.

## Timeline

No dated milestones are specified in the project specification.

## Effort metrics

Measured values only; a value that has not been measured stays "pending measurement".

| Metric | Value |
|---|---|
| Tokens (input / output) | 1963599 / 118926 |
| Hours (human) | pending measurement |
| Cost (USD) | 0.1286 |

## Factory run u293 (measured from API usage)

| Date (UTC) | Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|---|
| 2026-11-11 | generation | deepseek-v4-pro | yes | 5052 | 16839 | 0 | 0 | 0.0367 |
| 2026-11-11 | fix-1 | deepseek-flash | no | 28453 | 50634 | 0 | 1139968 | 0.0381 |
| 2026-11-11 | fix-2 | deepseek-flash | no | 8387 | 2286 | 0 | 27520 | 0.0027 |
| 2026-11-11 | audit | deepseek-flash | no | 30556 | 26531 | 0 | 402304 | 0.0217 |
| 2026-11-11 | fix-3 | deepseek-flash | no | 13126 | 9985 | 0 | 219776 | 0.0086 |
| 2026-11-11 | docs | deepseek-flash | no | 88201 | 12651 | 0 | 256 | 0.0208 |

Total: $0.1286. Prices: deepseek line, as measured by its adapter. Providers serve the current version of each model id, so the date tells which version answered; versions, launch stages and price sources per line are in the factory's model register (docs/MODELS.md).
