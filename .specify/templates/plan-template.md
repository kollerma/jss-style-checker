# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Standing gates derived from the project constitution (see
`.specify/memory/constitution.md`). Mark each PASS / FAIL / N/A and justify any
FAIL or deviation in the Complexity Tracking table.

- [ ] **§I Determinism**: No ML, heuristics, or nondeterministic logic inside
      any proposed rule `check` callable.
- [ ] **§II AST-First**: Each proposed rule uses pylatexenc or bibtexparser
      AST, or else explicitly justifies a raw-source scan (line width,
      trailing whitespace, byte-level encoding).
- [ ] **§III Non-Fatal Parse**: Plan records parse failures as `Violation`s;
      no code path raises out of the parse step.
- [ ] **§IV Zero Core Edits for Journals**: If this plan adds or changes a
      journal, no files under `src/texlint/core/` or `src/texlint/api.py` are
      modified. Journal wiring uses `importlib.metadata` entry points only.
- [ ] **§V Authority Cited**: Each new rule's metadata cites `jss.cls`,
      `article.tex`, the JSS style guide, or author instructions. Conflicts
      resolved per the §V priority order.
- [ ] **§VI ≥90% Precision Gate**: Plan references the eval corpus pass and
      explains how precision will be measured (`eval-jss report`) before the
      rule ships.
- [ ] **§VII Safe Auto-Fix**: Any `FixSuggestion` designed in this plan is
      self-verifying (re-check after apply) and writes via `tempfile` +
      `os.replace()`, or else sets `fix = None`.
- [ ] **§VIII TDD**: Tests are listed in `tasks.md` before the corresponding
      implementation tasks.
- [ ] **§IX Branch Coverage**: Plan commits to 100% branch coverage for every
      new or edited file under `src/texlint/journals/*/rules/`.
- [ ] **§X Small Surface**: No speculative helpers, shims, or dead code paths
      are introduced. Any new abstraction has at least three concrete callers.
- [ ] **§XII Reproducible Corpus**: If this plan introduces a precision claim,
      the corpus commit hash and manifest path are referenced.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
