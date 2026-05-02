# Project git hooks

Hooks shipped with the repo. The repo's `.githooks/pre-commit` (the
ruff + pytest hook activated via `git config core.hooksPath .githooks`)
already chains the iterate guard automatically — most contributors
don't need to install anything separately. The standalone scripts
here are for users who run a different hook driver, or who want to
wire the guard into a different spot.

## `pre-commit-guard`

Runs `eval-jss iterate guard` before allowing a commit. Refuses the
commit if any previously-passing rule regressed past the
`precision_drop_tolerance_pp` threshold in
`eval/iteration-policy.toml`. Skips the rescan for doc-only or
cosmetic commits (anything not touching `src/texlint/`, `eval/`, or
`tests/fixtures/{violations,recall}/`).

### Install — bare git

```bash
ln -s "$(pwd)/scripts/git-hooks/pre-commit-guard" .git/hooks/pre-commit
```

### Install — alongside existing hooks

If `.git/hooks/pre-commit` already exists (e.g. an Entire CLI hook),
chain it:

```bash
mv .git/hooks/pre-commit .git/hooks/pre-commit.local
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
"$(git rev-parse --show-toplevel)/.git/hooks/pre-commit.local" || exit $?
"$(git rev-parse --show-toplevel)/scripts/git-hooks/pre-commit-guard" || exit $?
EOF
chmod +x .git/hooks/pre-commit
```

### Install — via `core.hooksPath`

```bash
git config core.hooksPath scripts/git-hooks
```

(Note: this redirects ALL hooks to `scripts/git-hooks/`; only do this
if you don't have other system-installed hooks you want to keep.)

### Bypass (for intentional regressions)

```bash
SKIP_EVAL_JSS_GUARD=1 git commit -m "..."
```

Use sparingly; the regression then needs a follow-up commit that
restores the rule's precision or a documented relaxation of the
policy.

### Exit codes

| Code | Meaning |
|---:|---|
| 0 | Commit allowed (no regression OR doc-only change) |
| 1 | Regression detected; commit blocked |
| 2 | Runtime error (missing venv, missing `eval-jss` CLI) |
