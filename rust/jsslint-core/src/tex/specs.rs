//! Known macro/environment argument specs — compiled in from
//! `specs/003-jss-rule-catalogue/latex-macro-specs.json` by `build.rs`.
//!
//! That JSON is mechanically extracted from `pylatexenc`'s own default
//! context database (`tools/generate_latex_specs_json.py`), not
//! hand-copied — see that script's docstring. A macro/environment
//! *absent* from this table is "unknown" to the tokenizer, matching
//! `pylatexenc`: it takes zero arguments, and whatever follows (e.g. a
//! `{...}` group) parses as an ordinary sibling node. `_helpers.py`'s
//! `_macro_args_text` sibling-group fallback (see `crate::tex::prose`)
//! exists precisely because JSS's own macros (`\pkg`, `\proglang`,
//! `\code`, ...) are unknown in this sense.
//!
//! Argspec encoding (matches `pylatexenc.macrospec.MacroStandardArgsParser`):
//! each character is one argument slot — `{` mandatory group, `[`
//! optional bracket group, `*` optional literal star.

use std::collections::HashMap;
use std::sync::LazyLock;

include!(concat!(env!("OUT_DIR"), "/latex_specs_data.rs"));

struct SpecTables {
    macros: HashMap<&'static str, &'static str>,
    verbatim_macros: std::collections::HashSet<&'static str>,
    environments: HashMap<&'static str, &'static str>,
    verbatim_environments: std::collections::HashSet<&'static str>,
}

static TABLES: LazyLock<SpecTables> = LazyLock::new(|| SpecTables {
    macros: MACROS.iter().copied().collect(),
    verbatim_macros: VERBATIM_MACROS.iter().copied().collect(),
    environments: ENVIRONMENTS.iter().copied().collect(),
    verbatim_environments: VERBATIM_ENVIRONMENTS.iter().copied().collect(),
});

/// The argspec string for a known macro, e.g. `"*[[{"` for `\citep`.
/// `None` means unknown (zero args to the tokenizer).
pub fn macro_argspec(name: &str) -> Option<&'static str> {
    TABLES.macros.get(name).copied()
}

pub fn is_verbatim_macro(name: &str) -> bool {
    TABLES.verbatim_macros.contains(name)
}

/// The argspec string for a known environment's `\begin{...}` args
/// (e.g. `"{"` for `tabular`'s column spec). `None` means no
/// environment-level args are expected (the overwhelmingly common case).
pub fn environment_argspec(name: &str) -> Option<&'static str> {
    TABLES.environments.get(name).copied()
}

pub fn is_verbatim_environment(name: &str) -> bool {
    TABLES.verbatim_environments.contains(name)
}

/// Literal "specials" tokens (`~`, `&`, `--`, `---`, `` `` ``, `''`,
/// `` !` ``, `` ?` ``), longest-first so prefix matching prefers e.g.
/// `"---"` over `"--"`.
pub fn specials() -> &'static [&'static str] {
    SPECIALS
}
