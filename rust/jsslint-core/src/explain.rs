//! Rule explanation renderer — mirrors `texlint/explain.py` (spec 009).
//!
//! `_guide_index.py`'s runtime `guide_section` → `guide_url` backfill
//! isn't ported: every current `catalogue.yaml` entry that sets
//! `guide_section` also sets `guide_url` directly (verified: zero
//! entries need the backfill), and this port's `RuleMeta.guide_url` is
//! already fully populated from `catalogue.yaml` by `build.rs`.

use crate::catalogue::{self, RuleMeta};

/// Mirrors `explain.py::did_you_mean` (`difflib.get_close_matches`,
/// `n=5, cutoff=0.6`, candidates = every catalogue rule id).
pub fn did_you_mean(unknown_id: &str) -> Vec<String> {
    let candidates: Vec<&str> = catalogue::all_rules().iter().map(|r| r.rule_id).collect();
    close_matches(unknown_id, &candidates, 5, 0.6)
}

/// Mirrors `difflib.get_close_matches`: ASCII-safe (rule ids and their
/// typo'd lookalikes are always ASCII, so byte-sequence `ratio()` is
/// equivalent to Python's char-sequence `ratio()`). Not reusing the
/// `difflib` crate's own `get_close_matches` — it sorts ties by ratio
/// only (stable on iteration order), whereas Python's
/// `heapq.nlargest(n, result)` on `(ratio, x)` tuples breaks ties by
/// comparing `x` too (descending), which changes suggestion order
/// whenever two candidates tie on ratio.
fn close_matches(word: &str, candidates: &[&str], n: usize, cutoff: f32) -> Vec<String> {
    let mut scored: Vec<(f32, &str)> = candidates
        .iter()
        .filter_map(|&cand| {
            let mut matcher = difflib::sequencematcher::SequenceMatcher::new(cand, word);
            let ratio = matcher.ratio();
            if ratio >= cutoff {
                Some((ratio, cand))
            } else {
                None
            }
        })
        .collect();
    scored.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap().then_with(|| b.1.cmp(a.1)));
    scored.truncate(n);
    scored.into_iter().map(|(_, s)| s.to_string()).collect()
}

fn render_one_terminal(rule_id: &str, meta: &RuleMeta) -> String {
    let mut lines = vec![
        format!("{rule_id} ({})", meta.severity.as_str().to_uppercase()),
        format!("  Category: {}", meta.category),
        format!("  Authority: {} ({})", meta.authority, meta.authority_ref),
    ];
    if meta.confidence != "high" {
        lines.push(format!(
            "  Confidence: {} (measured corpus precision below the gate; see eval/improvement-log.md)",
            meta.confidence
        ));
    }
    if !meta.guide_section.is_empty() {
        lines.push(format!("  JSS guide: {}", meta.guide_section));
        if let Some(url) = meta.guide_url {
            lines.push(format!("  See: {url}"));
        }
    }
    lines.push(String::new());
    let body = if !meta.explanation.is_empty() {
        meta.explanation
    } else {
        meta.message_template
    };
    lines.push(body.to_string());
    lines.join("\n") + "\n"
}

fn render_one_markdown(rule_id: &str, meta: &RuleMeta) -> String {
    let mut parts = vec![format!("# {rule_id}"), String::new()];
    parts.push(format!("- **Severity:** {}", meta.severity.as_str()));
    parts.push(format!("- **Category:** {}", meta.category));
    parts.push(format!(
        "- **Authority:** {} ({})",
        meta.authority, meta.authority_ref
    ));
    if meta.confidence != "high" {
        parts.push(format!("- **Confidence:** {}", meta.confidence));
    }
    if !meta.guide_section.is_empty() {
        if let Some(url) = meta.guide_url {
            parts.push(format!("- **JSS guide:** [{}]({url})", meta.guide_section));
        } else {
            parts.push(format!("- **JSS guide:** {}", meta.guide_section));
        }
    }
    parts.push(String::new());
    let body = if !meta.explanation.is_empty() {
        meta.explanation
    } else {
        meta.message_template
    };
    parts.push(body.to_string());
    parts.push(String::new());
    parts.join("\n")
}

fn render_listing(fmt: &str) -> String {
    use std::collections::BTreeMap;
    let mut by_category: BTreeMap<&str, Vec<&str>> = BTreeMap::new();
    for meta in catalogue::all_rules() {
        by_category
            .entry(meta.category)
            .or_default()
            .push(meta.rule_id);
    }
    for ids in by_category.values_mut() {
        ids.sort_unstable();
    }

    let mut out: Vec<String> = Vec::new();
    if fmt == "markdown" {
        out.push("# JSS-lint rule catalogue\n".to_string());
    } else {
        out.push("JSS-lint rule catalogue:\n".to_string());
    }

    for (category, rule_ids) in &by_category {
        if fmt == "markdown" {
            out.push(format!("## {category}\n"));
            for rid in rule_ids {
                let meta = catalogue::lookup(rid).expect("catalogue rule");
                out.push(format!("- `{rid}` — {}", meta.message_template));
            }
            out.push(String::new());
        } else {
            out.push(format!("  {category}:"));
            for rid in rule_ids {
                let meta = catalogue::lookup(rid).expect("catalogue rule");
                out.push(format!("    {rid}  {}", meta.message_template));
            }
            out.push(String::new());
        }
    }

    let joined = out.join("\n");
    if fmt == "markdown" {
        joined + "\n"
    } else {
        joined
    }
}

/// Renders a rule explanation, or a per-category listing when
/// `rule_id` is `None`. `Err(normalized_id)` for an unknown rule id —
/// mirrors `explain.py::render`'s `raise KeyError(rule_id)`, with the
/// caller (CLI dispatch) producing a "did you mean?" suggestion list.
pub fn render(rule_id: Option<&str>, fmt: &str) -> Result<String, String> {
    let Some(raw_id) = rule_id else {
        return Ok(render_listing(fmt));
    };
    let normalized = raw_id.trim().to_uppercase();
    let Some(meta) = catalogue::lookup(&normalized) else {
        return Err(normalized);
    };
    if fmt == "markdown" {
        Ok(render_one_markdown(&normalized, meta))
    } else {
        Ok(render_one_terminal(&normalized, meta))
    }
}
