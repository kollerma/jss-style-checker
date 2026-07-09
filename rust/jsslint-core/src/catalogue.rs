//! Rule metadata catalogue — compiled in from
//! `specs/003-jss-rule-catalogue/catalogue.yaml` by `build.rs`.
//!
//! Mirrors `texlint.journals.jss._catalogue_data` (itself generated from
//! the same YAML by `tools/generate_catalogue_data.py`). Both languages
//! read the identical source of truth; neither hand-maintains a copy.

use crate::report::Severity;
use std::collections::HashMap;
use std::sync::LazyLock;

#[derive(Debug, Clone, Copy)]
pub struct RuleMeta {
    pub rule_id: &'static str,
    pub category: &'static str,
    pub severity: Severity,
    pub message_template: &'static str,
    pub authority: &'static str,
    pub inspects: &'static [&'static str],
    pub auto_fixable: bool,
    /// Measured-precision confidence tier: "high" / "medium" / "low".
    /// "high" is the catalogue default for rules without a narrowed tier.
    pub confidence: &'static str,
    /// JSS author-guide section label; "" for tool-side / un-backfilled rules.
    pub guide_section: &'static str,
    /// Absolute URL into the public JSS author guide; `None` for
    /// tool-side / un-backfilled rules.
    pub guide_url: Option<&'static str>,
}

include!(concat!(env!("OUT_DIR"), "/catalogue_data.rs"));

static RULES_BY_ID: LazyLock<HashMap<&'static str, &'static RuleMeta>> =
    LazyLock::new(|| RULES.iter().map(|r| (r.rule_id, r)).collect());

/// Look up a rule's catalogue metadata by id. `None` for unknown ids
/// (e.g. the synthetic `JSS-PARSE-000`, which has no catalogue entry —
/// callers fall back to `RuleMeta`-shaped defaults, matching
/// `output/json_output.py`'s `_catalogue().get(rule_id, {})`).
pub fn lookup(rule_id: &str) -> Option<&'static RuleMeta> {
    RULES_BY_ID.get(rule_id).copied()
}
