# Roadmap to indispensable

This directory captures the plan to evolve `jss-style-checker` from a
useful CLI into a tool a JSS author can't imagine writing without.

Twelve features in five phases. Each is fully specified with three
copy-paste prompts that drive the existing Spec Kit pipeline:
`/speckit.specify` -> `/speckit.clarify` -> `/speckit.plan`.

## Feature index

| # | Feature | Phase | Depends on |
|---|---|---|---|
| [006](006-sarif-output.md) | SARIF output | Foundations | — |
| [007](007-jss-guide-mapping.md) | JSS-guide rule mapping | Foundations | — |
| [008](008-auto-fix.md) | Auto-fix (`--fix` / `--dry-run` / `--apply`) | Author UX | — |
| [009](009-explain-command.md) | `jss-lint explain` subcommand | Author UX | 007 |
| [010](010-init-onboarding.md) | `jss-lint init` interactive bootstrap | Author UX | — |
| [011](011-language-server.md) | Language Server (LSP) | Editor experience | 006, 008 |
| [012](012-vscode-extension.md) | VS Code extension | Editor experience | 011 |
| [013](013-multi-file-projects.md) | Multi-file `\input`/`\include` resolver | Editor experience | — |
| [014](014-github-action.md) | Reusable GitHub Action | CI / journal | 006 |
| [015](015-conformance-report.md) | One-page editor conformance report | CI / journal | 007 |
| [016](016-revision-diff.md) | `jss-lint diff` between runs | CI / journal | — |
| [017](017-recall-evaluation.md) | Recall measurement + README badge | Trust | — |

## Recommended order

The table is in dependency order. You can interleave when convenient
(e.g., 008 before 007 if a contributor wants to start on auto-fix),
but later specs reference upstream specs in their prompts.

## Why this list

Short version of the rationale: 006 and 007 are foundations the rest
build on. 008-010 close the author-side workflow. 011-013 put the
linter inside the editor. 014-016 put it inside the journal review
process. 017 publishes the trust metric (recall) that converts
adoption hesitation into adoption.

The long version is in the contest-review notes that produced this
roadmap (see the PR description for `claude/review-contest-entries-*`).

## How to run a single feature

Each feature file is structured as three numbered prompt blocks. To
run one feature end-to-end inside Claude Code:

1. Open the feature file (e.g., `roadmap/006-sarif-output.md`).
2. Copy the section under `## /speckit.specify prompt` and paste it
   into Claude Code immediately after typing `/speckit.specify` (or
   include the slash command in the paste).
3. Wait for the spec branch + `spec.md` to be created.
4. Repeat for the `## /speckit.clarify prompt` section.
5. Repeat for the `## /speckit.plan prompt` section.
6. From there, the existing `/speckit.tasks` and `/speckit.implement`
   workflow takes over — same as for specs 001-005.

## How to run the entire roadmap unattended

Open a Claude Code session in the repo root and paste this single
bootstrap message:

```
Read roadmap/README.md and roadmap/00X-*.md in numerical order. For
each feature file, run the three Spec Kit slash commands in this
order:

  1. /speckit.specify with the contents of the
     "/speckit.specify prompt" section.
  2. /speckit.clarify (no args). Answer with sensible defaults from
     the feature file when blocked; otherwise propagate the question
     and stop for me.
  3. /speckit.plan with the contents of the
     "/speckit.plan prompt" section.

After each phase, commit the generated files with the message
"speckit(00X-feature-name): <phase>". Continue to the next feature
only after all three phases for the current feature have committed
cleanly. Stop and surface anything ambiguous before guessing.
```

Claude Code drives the Spec Kit pipeline through every feature,
producing the same `specs/00X-*/` layout that 001-005 already use.

## Bumping the roadmap

When a feature ships, leave its file in place but prepend a status
banner:

```
> **Status:** shipped in `specs/006-sarif-output/`
> **End-of-spec summary:** [link]
```

When scope changes mid-roadmap, edit the feature file directly rather
than accumulating diffs. The roadmap is intent, not history; history
lives under `specs/` and `CHANGELOG.md`.

## Tracking deferred work

Each feature shipped its core correctness surface (engine + tests).
Subsidiary work that the v1 implementation deferred — CLI
sub-group migration, marketplace publishes, hand-annotated
corpora, full catalogue backfills — lives in
[`follow-ups.md`](follow-ups.md). Check items off there as they
land.
