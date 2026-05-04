# Research: SARIF 2.1.0 Output

**Phase**: 0 (Outline & Research)
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

This file resolves the open decisions identified during planning that
were too implementation-shaped for the spec.

---

## 1. Why SARIF 2.1.0 specifically (not 2.0, not draft-3.0)

**Decision**: Target SARIF 2.1.0, OASIS Standard published 2020-03-27,
schema URL `https://json.schemastore.org/sarif-2.1.0.json`.

**Rationale**:
- 2.1.0 is what GitHub code scanning consumes; uploads against the
  CodeQL action are validated against 2.1.0.
- 2.0 is superseded; tooling that reads it accepts 2.1.0
  transparently.
- SARIF 3.x is draft-only as of writing and not consumed by the
  surfaces we want to plug into (GitHub, VS Code SARIF Viewer,
  CodeQL, Sonar).

**Alternatives considered**:
- SARIF 2.0: rejected. Adds nothing 2.1.0 doesn't already cover,
  and produces format-version drift in stored artefacts over time.
- Custom JSON schema (extend `--output json`): rejected per spec
  rationale — every consumer would need glue code.

---

## 2. Schema validation: vendor or fetch?

**Decision**: Vendor the SARIF 2.1.0 JSON schema as a test fixture
at `tests/fixtures/sarif-2.1.0-schema.json`. Schema validation is
performed via `jsonschema` (already a dev extra; not a runtime dep).

**Rationale**:
- Constitution §I (determinism) prohibits network IO inside test
  runs — a fetched schema would tie test reproducibility to
  upstream availability.
- The OASIS schema is stable; vendoring it means we pin a known
  version and update it deliberately.
- The vendored file is JSON, not generated; reviewers can diff it.

**Alternatives considered**:
- Use `jsonschema` with the `$id` URL and let it auto-fetch:
  rejected — flaky CI, opaque test failures when offline.
- Skip schema validation and assert structure manually: rejected
  — the schema is the contract; manual structural assertions
  drift from the schema and catch fewer regressions.

---

## 3. Path normalisation for `artifactLocation.uri`

**Decision**: All artifact URIs are POSIX-style relative paths
computed by `Path.relative_to(source_root)` when the file lives
under `source_root`, falling back to `os.path.relpath(file,
source_root)` (which uses `..` segments) when it does not.
Absolute paths are never emitted.

**Rationale**:
- GitHub code scanning resolves SARIF `artifactLocation.uri`
  against the repo root. Relative POSIX paths are the
  format-canonical form.
- POSIX-style separators are deterministic across Linux, macOS,
  and Windows hosts producing the same artefact (matches
  `json_output.py`'s use of `Path.as_posix()`).
- `os.path.relpath` is the standard library idiom for "relative
  path with `..` segments". The alternative — `Path.resolve()`
  followed by manual prefix stripping — is more error-prone.

**Alternatives considered**:
- Always emit absolute paths: rejected — defeats the purpose of
  `--source-root`; GitHub code scanning fails to match files.
- Refuse to emit paths outside the source root (raise): rejected
  — surprising in monorepo layouts; also violates Constitution
  §III (the renderer should never raise on a complete report).
- Use the `file://` scheme: rejected — SARIF allows scheme-less
  URIs and GitHub specifically prefers them as relative.

---

## 4. Category → SARIF properties: `tags` vs `taxonomies`

**Decision**: Emit each rule's category as a single string under
`tool.driver.rules[].properties.tags = [<category>]`. Do NOT emit a
SARIF `taxonomies` array.

**Rationale**:
- SARIF `taxonomies` are reserved for cross-tool standards (CWE,
  OWASP, MISRA). JSS rule categories (`markup`, `style`,
  `naming`, `preamble`, …) are tool-internal and have no
  cross-tool meaning.
- `properties.tags` is the SARIF-blessed surface for tool-
  specific labels and is what GitHub displays in the "Severity"
  / "Tags" filter UI.
- Emitting a fake taxonomy would mislead consumers into
  treating these as standard identifiers.

**Alternatives considered**:
- Emit as `taxa[]` under a homemade `taxonomies[0]`: rejected per
  rationale above — semantic abuse of the SARIF surface.
- Emit as `properties.category` (custom field): rejected — SARIF
  validators ignore unknown properties, but `tags` is the
  documented place for this.

---

## 5. `--source-root` default and behaviour for non-SARIF outputs

**Decision**: Default to `Path.cwd()`. Silently accept (and ignore)
the flag for `--output terminal|json|html` so a single CI
invocation can pass it unconditionally.

**Rationale** (default):
- CWD is what the user types from. The first-input-file's
  directory shifts URIs unexpectedly when multi-file invocations
  span directories. Spec Clarifications resolved this.

**Rationale** (silent acceptance):
- A CI pipeline that runs the linter once and selects the
  output format from a config matrix needs the flag to be
  uniformly safe to pass. Erroring would force callers to
  branch on output format.
- The flag has no observable effect for non-SARIF outputs;
  documenting the silent-accept behaviour in `--help` is
  sufficient.

**Alternatives considered**:
- Default to first-input-file's directory: rejected per spec
  Clarifications.
- Reject the flag for non-SARIF outputs: rejected per silent-
  acceptance rationale.
- Make the flag mandatory for SARIF: rejected — defeats zero-
  config use of `--output sarif` from the repo root.

---

## 6. `JSS-PARSE-000` placement: `results` vs `notifications`

**Decision**: Emit parse failures as
`runs[0].invocations[0].toolExecutionNotifications[]` entries with
`descriptor.id = "JSS-PARSE-000"`, `level = "error"`, and the
artifact URI in `locations[0]`. Do NOT also emit them as
`runs[0].results` entries.

**Rationale**:
- SARIF distinguishes "findings" (`results`) from "tool-
  execution events" (`notifications`). A file the linter could
  not analyse is the latter — every other rule failed to fire
  on it because the file never reached the analysis stage.
- GitHub code scanning treats `notifications` differently from
  `results`: notifications surface as workflow run warnings,
  not as inline-diff annotations. That matches the user
  expectation — a parse failure is "the file is broken", not
  "line 42 has a problem".
- Spec Clarifications recorded that `--ignore-rules
  JSS-PARSE-000` does NOT silence the notification (otherwise
  users could mute the linter on broken files).

**Alternatives considered**:
- Emit in both `results` and `notifications`: rejected — would
  double-count and break the result-count semantics relied on
  by spec 014 (GitHub Action) and spec 016 (revision-diff).
- Emit only in `results`: rejected — wrong SARIF semantics;
  GitHub would surface it as an inline annotation on a file it
  could not analyse.

---

## 7. Renderer module shape: dataclasses vs dict construction

**Decision**: Construct the SARIF document as a nested `dict[str,
Any]` directly in `output/sarif.py`. Do NOT introduce a `SarifLog`
/ `SarifRun` / `SarifResult` dataclass hierarchy.

**Rationale**:
- Constitution §X (small surface): the renderer is a single
  one-shot projection; a class hierarchy adds surface without
  adding semantics. `json_output.py` and `html_output.py`
  follow the same dict-only pattern.
- A schema-validated golden fixture is a stronger contract than
  a hand-typed dataclass hierarchy.
- A dataclass hierarchy would need to mirror SARIF 2.1.0's
  ~100 type names and would re-bind us to the schema in two
  places.

**Alternatives considered**:
- Wrap the official `sarif-om` Python types: rejected — adds a
  runtime dep, contradicts the plan's "no new runtime deps"
  constraint, and the type surface is excessive for our use
  (we render <10 of the ~100 SARIF types).
- Hand-roll dataclasses: rejected per surface argument above.

---

## 8. Test fixture strategy

**Decision**: Four golden fixtures under `tests/fixtures/sarif/`,
each produced by running the renderer on a known input + asserted
byte-equal against the file. Updates require regenerating the
goldens via a `pytest --update-goldens` flag (or equivalent —
plan-level micro-decision).

**Rationale**:
- Byte-equality against a stored artefact is the strongest
  determinism check (Constitution §I).
- Schema validation runs on the same generated bytes, so a
  golden update that breaks the schema fails the schema test
  without escaping review.
- The four scenarios (clean, single-error, multi-file,
  parse-error) cover the four code paths: empty results, a
  single result with a region, multi-file URI handling, and
  the notifications/results split.

**Alternatives considered**:
- Programmatic structural assertions: rejected — drift-prone
  and weaker than byte-equality.
- Snapshot testing via syrupy: rejected — adds a dev dep for a
  capability the four-file plain-text approach already has.

---

## Summary

All eight decisions are downstream of either the spec
Clarifications (§5, §6, §4) or Constitution principles I, III,
and X (§3, §7, §2). No remaining `NEEDS CLARIFICATION` markers.
Ready for Phase 1.
