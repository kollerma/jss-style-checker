# `project` fixtures

`JSS-PROJECT-001` (cycle) and `JSS-PROJECT-002` (missing reference) are
graph-level: they fire via `Rule.check_project` against a whole
`ParsedProject` built by `texlint.core.resolver.resolve` from a *pair*
of files (or more), not via `Rule.check` against one isolated file.
They're therefore exempt from the single-file `-bad`/`-good` convention
used elsewhere in this directory (see
`tests/integration/test_full_catalogue_coverage.py`'s
`_PROJECT_LEVEL_CATEGORIES` skip) and covered instead by
`tests/unit/journals/jss/rules/test_project.py` and the multi-file
fixtures under `tests/fixtures/resolver_projects/`.

This directory exists so `test_every_category_has_a_fixture_directory`
finds one per `ROLLOUT_ORDER` category.
