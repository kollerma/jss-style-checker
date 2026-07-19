# Contributing

Thanks for your interest! Two documents govern how this repo works — read
them before a non-trivial change:

- `.specify/memory/constitution.md` — the project's non-negotiable
  principles (determinism, per-rule precision gates, engine parity, …).
- `CLAUDE.md` — the working invariants and everyday commands in short form.

## Setup

```sh
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]' -e tests/fixtures/stub_journal
git config core.hooksPath .githooks     # activates the pre-commit gates
```

The Rust workspace needs a stable Rust toolchain (`rustup`); the R package
additionally needs R ≥ 4.2 and Cargo.

## Before you open a PR

Run the same gates CI runs:

```sh
export PATH="$PWD/.venv/bin:$HOME/.cargo/bin:$PATH"   # both matter
ruff check .
python -m pytest tests/ -q
(cd rust && cargo fmt --all --check && cargo clippy --workspace --all-targets --locked -- -D warnings)
(cd rust && cargo test --workspace --locked)
```

Three rules that catch most first-time contributors:

1. **Engine parity (Constitution §XIII).** Any change to rule or
   user-visible behavior must land in *both* engines — Python
   (`src/texlint/`) and Rust (`rust/jsslint-core/`) — with parity-suite
   coverage keeping their output byte-identical. The corpus-backed parity
   tests skip on a fresh clone; materialize the corpus with
   `.venv/bin/eval-jss corpus fetch` and
   `python -m eval.recall_corpus_scaffold` to run them locally. If Python
   parity tests fail unexpectedly, rebuild the in-process oracle first:
   `(cd rust/jsslint-py && maturin develop --release)` — a stale build is
   the usual culprit.
2. **Never hand-edit a version string (Constitution §XV).** Edit `VERSION`
   and run `python scripts/set_version.py`.
3. **No network or filesystem code in the portable core (Constitution
   §XIV).** Network belongs in `rust/jsslint-crossref/` (CLI-only);
   filesystem concerns belong at the CLI/binding layer. A CI guard test
   enforces the dependency graph.

New lint rules additionally require: a cited authority (§V), a failing test
first (§VIII), 100% branch coverage on the Python rule module (§IX), and a
≥90% precision measurement on the eval corpus (§VI) — see the constitution
for the details.

## Security

See [SECURITY.md](SECURITY.md) — please report vulnerabilities privately.
