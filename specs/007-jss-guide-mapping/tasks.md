---

description: "Tasks for JSS-guide rule mapping"
---

# Tasks: JSS-guide Rule Mapping

**Input**: Design documents from `/specs/007-jss-guide-mapping/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/catalogue-citation.md

**Tests**: Contract tests (`tests/unit/test_catalogue.py`) are
mandatory per Constitution §VIII; one test per invariant from
`contracts/catalogue-citation.md`. Renderer regression tests for
the four output surfaces (terminal / JSON / SARIF / HTML).

## Phase 1: Setup

- [x] T001 Create `docs/jss-guide/index.json` with the initial
      section→URL map. Seed with 5–10 high-traffic sections; the
      complete map fills in via the catalogue backfill.

## Phase 2: Foundational

- [x] T002 Add `guide_section: str = ""` and
      `guide_url: str \| None = None` fields to the `Rule`
      dataclass in `src/texlint/api.py`.
- [x] T003 Extend the catalogue YAML schema in
      `tools/_catalogue_validate.py` to include the two new
      OPTIONAL keys; do NOT make them REQUIRED yet (rollout
      tolerance).
- [x] T004 Update `tools/generate_catalogue_data.py` to emit
      the two new fields when present in YAML; default to empty
      string / `None` when absent.
- [x] T005 Re-run `python -m tools.generate_catalogue_data` and
      commit the regenerated `_catalogue_data.py`.
- [x] T006 Create `src/texlint/journals/jss/_guide_index.py`
      exposing `load_guide_index() -> dict[str, str]` per
      data-model §4.

## Phase 3: User Story 1 — Terminal cite suffix (P1)

- [x] T007 [US1] Update `src/texlint/output/terminal.py` to
      append `(see <guide_section>)` when the rule's
      `guide_section` is non-empty and not the sentinel
      `"internal"`.
- [x] T008 [US1] Add a regression test
      `tests/integration/test_cli_author_terminal.py::test_cite_suffix_present`
      using a backfilled fixture rule.

## Phase 4: User Story 2 — Renderer plumbing (P1)

- [ ] T009 [US2] Update `src/texlint/output/json_output.py` to
      include `guide_section` and `guide_url` per violation entry
      (default empty string / `null`).
- [x] T010 [US2] Update `src/texlint/output/sarif.py` to populate
      `tool.driver.rules[].helpUri` from `Rule.guide_url` when
      non-`None` and append the section to
      `shortDescription.text` when present.
- [x] T011 [US2] Update `src/texlint/output/html_output.py` to
      render `guide_section` as `<a href="guide_url">` when both
      are set (sentinel rules render as plain text).
- [x] T012 [US2] Regenerate JSON / HTML / SARIF golden fixtures
      that reference the new fields.

## Phase 5: User Story 3 — Catalogue contract test (P1)

- [x] T013 [US3] Create `tests/unit/test_catalogue.py::
      test_every_rule_has_optional_citation_or_sentinel` per the
      lenient v1 enforcement (warns when a citable rule's
      `guide_url is None`; hard-fails when a tool-side rule
      has a non-sentinel value).
- [x] T014 [US3] Add `tests/unit/test_catalogue.py::
      test_guide_urls_resolve_through_index` that, for every
      backfilled rule, asserts the URL matches
      `_guide_index.load_guide_index()[guide_section]`.

## Phase 6: User Story 4 — Centralised URL update (P2)

- [ ] T015 [US4] Document the `index.json` re-publication flow
      in `docs/jss-guide/README.md` (small file; one section
      per data-model §4).

## Phase 7: Polish

- [x] T016 [P] Run the full test suite (`pytest -q`) and confirm
      no regressions.
- [x] T017 [P] Mark a follow-up "complete catalogue backfill" task
      in the project tracker; the spec-007 PR ships the
      infrastructure plus a partial backfill of high-priority
      rules (FR-011 spec target is full backfill; v1 ship can
      do a partial backfill with a clear follow-up).

## Dependencies

```
T001-T006 are setup; T002 (Rule fields) blocks all renderer changes.
T007-T012 are renderer plumbing; can run in parallel after T006.
T013-T014 are the contract-test surface; can run in parallel.
```

## Implementation Strategy

**MVP**: Phases 1, 2, parts of 3, 4, 5. Ship the infrastructure
(Rule fields + index.json + contract tests + renderer plumbing).
Per the spec author's pragmatism, the FULL 58-rule backfill is
a separate mechanical PR cited as a follow-up; v1 implementation
ships the citation surface ready for that backfill.
