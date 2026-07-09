//! Phase 4 stub. The real CLI (bare-lint + `explain`/`init`/`report`/
//! `diff`/`lsp`, matching `texlint.cli`) lands once the rule engine
//! exists (plan Phases 1-3). For now this only proves the workspace
//! wires together end to end: `jsslint-core`'s JSON renderer runs and
//! its output is byte-verified against the real `jss-lint` in
//! `jsslint-core/tests/parity.rs`.

fn main() {
    eprintln!("jsslint: core engine not yet implemented (spec 018, Phase 1-3 pending)");
    std::process::exit(2);
}
