<!-- SPECKIT START -->
Constitution (project invariants): `.specify/memory/constitution.md` (v1.1.0).
Spec history: `specs/001-…/` through `specs/017-…/` (Python linter roadmap,
complete), `specs/018-rust-core/` (Rust multi-engine port, retroactive
record), `specs/023-…/`–`specs/026-…/` (post-1.0 features, retroactive
records). Numbers 019–022 were paper/doc branches with no spec artifacts.
Deferred work is tracked in `roadmap/follow-ups.md`.
<!-- SPECKIT END -->

# Working in this repo

Two engines, one behavior. `src/texlint/` (Python) is the reference
implementation; `rust/` is a workspace porting it to a CLI (`jsslint-cli`),
browser/npm WASM (`jsslint-wasm`, also powering `web/` and
`vscode-extension/`), a PyO3 wheel (`jsslint-py`), and an R package
(`r/jsslintr/`, which vendors the core via
`r/jsslintr/tools/vendor-jsslint-core.sh`). See `rust/README.md` for the
tool-by-tool guide.

Non-negotiable invariants (Constitution §XIII–§XV — CI-enforced, don't fight
the guards, fix the cause):

- **Engine parity**: any rule/behavior change lands in BOTH engines and must
  keep `terminal`/`json`/`sarif`/`html` output byte-identical. Enforced by
  `rust/*/tests/*_parity.rs`, `tests/unit/test_jsslint_parity.py`, and the R
  testthat suite (all skip cleanly when the gitignored eval corpus isn't
  materialized — `eval-jss corpus fetch` + `python -m
  eval.recall_corpus_scaffold` to fetch it).
- **Portable-core isolation**: no network/filesystem code in `jsslint-core`,
  `jsslint-wasm`, `jsslint-py`, or the vendored R crate. Network lives in
  `rust/jsslint-crossref/` (CLI-only); filesystem concerns live at the
  CLI/binding layer. Guarded by `rust/jsslint-wasm/tests/isolation.rs`.
- **Single-source version**: edit `VERSION` and run
  `python scripts/set_version.py` — never hand-edit a manifest version.
  Guarded by `tests/unit/test_version_single_source.py`.

Everyday commands (venv at `.venv`, Python 3.12):

```sh
export PATH="$PWD/.venv/bin:$HOME/.cargo/bin:$PATH"   # both needed
python -m pytest tests/ -q            # Python suite (needs .venv/bin on PATH:
                                      #   eval tests shell out to `jss-lint`)
ruff check .                          # lint gate (CI runs exactly this)
python -m pytest tests/unit/journals/jss/ \
    --cov=src/texlint/journals/jss/rules --cov-branch   # §IX rule coverage
(cd rust && cargo test --workspace)   # Rust suite incl. parity + isolation
R CMD INSTALL --library=$HOME/R/library r/jsslintr   # R package build
```

Two virtualenvs live side by side: **`.venv`** is the one to use (Linux
containers and CI create it); **`.venv-host`** is a macOS host venv used by
the paper toolchain, and its interpreter is a dangling symlink anywhere but
that host. `paper/Makefile` and `paper/regenerate.sh` prefer `.venv-host`
only when it actually executes and fall back to `.venv`. Never rebuild
`.venv-host` from a container — the working tree is shared with the host.

Rule unit tests mirror the rule modules: `tests/unit/journals/jss/rules/
test_<category>.py` for `src/texlint/journals/jss/rules/<category>.py`
(they lived in `tests/unit/rules/` until spec 027; older specs still name
that path).

Release flow: tag-triggered workflows publish per component
(`vX.Y.Z-cli|-py|-pypkg|-wasm|-vscode`, plain `vX.Y.Z` for the Action —
push tags to the public remote only). PyPI/npm use OIDC trusted publishing.
`vscode-extension/` runs the checker in-process from the bundled WASM
(`npm run build:wasm`); it has no Python or binary dependency.
