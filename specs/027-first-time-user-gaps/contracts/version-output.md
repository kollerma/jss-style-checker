# Contract: `--version` output and binding version functions

**Plan**: [../plan.md](../plan.md) §4

## C-1 Block

`jss-lint --version` and `jsslint --version` print exactly four lines to
stdout, each terminated by `\n`, and exit 0:

```
jss-lint 1.2.0
engine: texlint/python 1.2.0
rule set: 2026-09-15 (jss.cls 3.3, vendored 2021-05-23)
journal: jss
```

Rust prints `engine: jsslint-core/rust 1.2.0` on line 2. Lines 1, 3, and
4 are byte-identical across engines; line 2 is the one documented
divergence (`version_parity.rs` masks it).

| Line | Source |
|---|---|
| 1 | program name is always `jss-lint`; version from `texlint.__version__` / `CARGO_PKG_VERSION` (single-sourced, §XV) |
| 2 | engine label + the same version |
| 3 | `ruleset_version`, `guide_edition`, `source_vendored_at` from the active journal's metadata |
| 4 | the journal id that would be used for a lint run |

## C-2 Journal resolution

`--version` is not eager: it is handled after `.jss-lint.toml` is loaded
and `--journal` is applied, so line 4 reflects the effective journal.

| Case | Line 3 | Line 4 |
|---|---|---|
| default | as above | `journal: jss` |
| a registered journal without metadata (e.g. the `stub` fixture) | `rule set: n/a` | `journal: stub` |
| `--journal nope` (not registered) | `rule set: n/a` | `journal: nope (not registered)` — still exit 0 |

## C-3 Formatter

`texlint.version.format_version_block(tool, engine, rule_set, journal)`
and `jsslint_core::version::format_block(..)` live in core and are the
only producers of the block, so the bindings reuse them.

## C-4 Binding version functions

| Binding | Call | Returns |
|---|---|---|
| WASM (`jsslint-wasm`) | `version()` | `{tool: "1.2.0", engine: "jsslint-core/rust", rulesetVersion: "2026-09-15", guideSource: "jss.cls 3.3 (2021-05-23)"}` |
| PyO3 (`jsslint`) | `jsslint.version()`; `jsslint.__version__` | the same keys as a `dict`; the version string |
| R (`jsslintr`) | `jsslint_version()` | named list with `package` (DESCRIPTION, e.g. `"1.2.0-1"`), `engine`, `tool`, `ruleset_version`, `guide_source` |

The R `package` field carries the CRAN resubmission suffix; this is the
distribution → engine → rule-set mapping in code. `docs/versions.md`
carries the same mapping for CTAN and the other channels.

## C-5 Tests

`rust/jsslint-cli/tests/version_parity.rs` compares lines 1, 3, 4 for the
default case, `--journal jss`, and a scratch directory whose
`.jss-lint.toml` sets `journal = "nope"`; `tests/unit/test_jsslint_parity.py`
compares `jsslint.version()["rulesetVersion"]` with `texlint`'s value.

## C-6 Backward compatibility

The previous one-line outputs (`jss-lint, version 1.1.0` / `jss-lint
1.1.0`) are replaced; scripts that parsed them should read line 1, whose
`jss-lint <semver>` shape is a superset of the old Rust form.
