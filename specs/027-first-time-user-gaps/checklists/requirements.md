# Specification Quality Checklist: Release 1.2.0 — first-time-user gaps

**Purpose**: Validate specification completeness and quality before proceeding to tasks
**Created**: 2026-09-06
**Feature**: [spec.md](../spec.md) · [plan.md](../plan.md)

## Content Quality

- [x] No implementation details in user stories (file paths and function names live in plan.md)
- [x] Focused on user value: each story names who benefits and what they can now do
- [x] Written for a reader who knows JSS submissions, not the codebase
- [x] All mandatory sections completed (stories, edge cases, requirements, entities, success criteria, assumptions)

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain; every open question was settled in the two review rounds and is listed under Clarifications
- [x] Requirements are testable and unambiguous (each FR names an observable output, exit code, file shape, or test)
- [x] Success criteria are measurable (counts, exit codes, byte equality, bundle size)
- [x] Success criteria are technology-agnostic where the property is (SC-001…SC-006, SC-010, SC-013); SC-008/SC-009 name the two engines because engine parity is itself the requirement
- [x] All acceptance scenarios are defined for every story
- [x] Edge cases are identified (stub journal, retired rule, renamed file, same-shape masking, parse errors, malformed baseline, Windows console, recall corpus growth)
- [x] Scope is clearly bounded (deferred: CLI zip, baseline in bindings, SARIF baselineState, nine deferred suggestion rules, second annotator)
- [x] Dependencies and assumptions identified (17-paper corpus, undated guide, Python-based Action, manual CRAN/CTAN)

## Decision Traceability

- [x] Every maintainer decision D1–D11 appears in Clarifications with its rationale
- [x] Rejected alternatives are recorded (research.md): snippet-hash key, message-only key, source-line context key, byte-identical coloured output, git-dirty refusal, stderr footer, 1.1.1 split, CLI zip, floor kept at 0.70
- [x] Empirical evidence is cited where a decision rests on it: five-paper simulated rounds, the four jss5342 revisions, the 30-paper suggestion audit, the item-S prototype (plan §5.7, §5A)
- [x] Item S's final scope (ten rules; `JSS-WIDTH-001` generic) matches the prototype result, not the pre-prototype list

## Constitution Alignment

- [x] §IV: journal-supplied metadata degrades gracefully for a third-party journal (Edge Cases, FR-A/FR-G)
- [x] §VIII/§IX: item S is the only change to rule modules and is stated as test-first with 100 % branch coverage (FR-S-004)
- [x] §XIII: byte-identity of the plain stream, JSON, SARIF, HTML, and baseline files is a requirement (SC-008); the coloured-bytes divergence is explicit (FR-F-004)
- [x] §XIV: baseline I/O, TTY detection, and zip handling are stated as CLI/web-layer concerns; no new core dependency (SC-012)
- [x] §XV: `ruleset_version` is described as data provenance, not a suite version

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows (clean run, reviewer mode, adoption, revision, fixing, pinning, colour, Overleaf)
- [x] Feature meets measurable outcomes defined in Success Criteria
- [ ] Coverage YAML curation complete (146 rows migrated, 15 unclaimed rules given directives, 7 retired credits re-judged) — implementation task, not a spec item
- [ ] Recall snapshot regenerated from a fresh recorded run and floor ratcheted — release task

## Notes

- The recall percentage formula (integer half-up) and the baseline key
  are contracts, not implementation prescriptions: both engines must
  agree on them byte for byte.
- The illustrative coverage counts in quickstart.md are placeholders
  until `guide-coverage.yaml` is curated.
