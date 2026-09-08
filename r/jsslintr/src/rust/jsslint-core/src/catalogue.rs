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
    pub authority_ref: &'static str,
    pub explanation: &'static str,
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

/// Provenance of the shipped recall run — mirrors `api.RecallRun`.
/// Field order matches the generated literal in `build.rs`.
#[derive(Debug, Clone, Copy)]
pub struct RecallRunData {
    pub run_timestamp: &'static str,
    pub corpus_hash: &'static str,
    pub min_plants: u32,
    pub papers: u32,
    pub tp: u32,
    pub fn_: u32,
}

include!(concat!(env!("OUT_DIR"), "/catalogue_data.rs"));

static RECALL_BY_ID: LazyLock<HashMap<&'static str, (u32, u32)>> =
    LazyLock::new(|| RECALL.iter().map(|(id, tp, f)| (*id, (*tp, *f))).collect());

/// Measured recall for one rule. `(0, 0)` — i.e. unmeasured — for a
/// rule the snapshot does not name.
pub fn recall(rule_id: &str) -> crate::report::RecallStat {
    let (tp, fn_) = RECALL_BY_ID.get(rule_id).copied().unwrap_or((0, 0));
    crate::report::RecallStat { tp, fn_ }
}

/// The recall run this build ships.
pub fn recall_run() -> crate::report::RecallRun {
    crate::report::RecallRun {
        run_timestamp: RECALL_RUN.run_timestamp.to_string(),
        corpus_hash: RECALL_RUN.corpus_hash.to_string(),
        min_plants: RECALL_RUN.min_plants,
        papers: RECALL_RUN.papers,
        tp: RECALL_RUN.tp,
        fn_: RECALL_RUN.fn_,
    }
}

static RULES_BY_ID: LazyLock<HashMap<&'static str, &'static RuleMeta>> =
    LazyLock::new(|| RULES.iter().map(|r| (r.rule_id, r)).collect());

/// Look up a rule's catalogue metadata by id. `None` for unknown ids
/// (e.g. the synthetic `JSS-PARSE-000`, which has no catalogue entry —
/// callers fall back to `RuleMeta`-shaped defaults, matching
/// `output/json_output.py`'s `_catalogue().get(rule_id, {})`).
pub fn lookup(rule_id: &str) -> Option<&'static RuleMeta> {
    RULES_BY_ID.get(rule_id).copied()
}

/// Every catalogue rule's metadata, in the generated (alphabetical by
/// id) order. Used by the SARIF renderer's `tool.driver.rules` array,
/// which must list every rule regardless of whether it fired.
pub fn all_rules() -> &'static [RuleMeta] {
    RULES
}

/// Journal rollout order — mirrors `_catalogue_data.ROLLOUT_ORDER`
/// (`journals/jss/__init__.py::JSSJournal.categories()` iterates this).
pub fn categories() -> &'static [&'static str] {
    CATEGORIES
}

/// Rule-set provenance for the built-in `jss` journal (spec 027 item D).
///
/// Mirrors `JSSJournal.metadata().rule_set` on the Python side. This
/// engine registers no other journal (a documented §IV deviation, see
/// `rust/README.md`), so there is no per-journal dispatch here — but
/// callers still route through `report::RuleSetInfo` so the surfaces
/// stay identical to Python's, where a third-party journal may supply
/// nothing.
pub fn rule_set() -> crate::report::RuleSetInfo {
    crate::report::RuleSetInfo {
        version: Some(RULESET_VERSION.to_string()),
        fingerprint: Some(RULESET_FINGERPRINT.to_string()),
        guide_edition: Some(GUIDE_EDITION.to_string()),
        source_vendored_at: Some(SOURCE_VENDORED_AT.to_string()),
        recall: Some(recall_run()),
    }
}
