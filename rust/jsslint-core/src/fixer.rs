//! Auto-fix engine — mirrors the pure conflict-resolution and
//! text-application logic in `core/fixer.py`. The file I/O, atomic
//! write, interactive prompting, and re-validation-by-re-running-the-
//! whole-engine parts of Python's `apply_fixes` are Phase 4 (CLI/
//! engine) concerns tied to a fully assembled rule engine that
//! doesn't exist yet in `jsslint-core` — this module ports only the
//! two pure, directly fixture-testable functions the porting plan
//! calls out: `_resolve_conflicts` and `_apply_to_text`.

use crate::report::{Fix, FixConfidence, Violation};

/// A violation reduced to what fix-application needs. Mirrors
/// `fixer.py::_Candidate`.
#[derive(Debug, Clone)]
pub struct Candidate {
    pub file: String,
    pub fix: Fix,
    pub rule_id: String,
    pub line: u32,
}

/// Every violation carrying a `Fix`, reduced to a `Candidate`. Mirrors
/// `fixer.py::_candidates`.
pub fn candidates_from_violations(violations: &[Violation]) -> Vec<Candidate> {
    violations
        .iter()
        .filter_map(|v| {
            v.fix.as_ref().map(|fix| Candidate {
                file: v.file.clone(),
                fix: fix.clone(),
                rule_id: v.rule_id.clone(),
                line: v.line,
            })
        })
        .collect()
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SkipReason {
    Conflict,
    RuleNotSelected,
    UserSkipped,
}

#[derive(Debug, Clone)]
pub struct FixSkip {
    pub file: String,
    pub fix: Fix,
    pub rule_id: String,
    pub reason: SkipReason,
}

/// Partition fixes for a single file into `(applied, skipped)`: sort
/// by `Fix.start`, scan and group overlapping intervals into
/// clusters, pick a deterministic winner per cluster (`safe`
/// confidence first, then `rule_id`, then `start`, then `end` — the
/// first cluster member wins any remaining full tie, matching
/// Python's `min()`). Mirrors `fixer.py::_resolve_conflicts`.
pub fn resolve_conflicts(candidates: Vec<Candidate>) -> (Vec<Candidate>, Vec<FixSkip>) {
    if candidates.is_empty() {
        return (Vec::new(), Vec::new());
    }
    let mut ordered = candidates;
    ordered.sort_by_key(|c| c.fix.start);

    let mut applied = Vec::new();
    let mut skipped = Vec::new();
    let mut cluster: Vec<Candidate> = Vec::new();
    let mut cluster_end: i64 = -1;

    for c in ordered {
        if c.fix.start as i64 >= cluster_end {
            flush_cluster(&mut cluster, &mut applied, &mut skipped);
            cluster_end = c.fix.end as i64;
            cluster.push(c);
        } else {
            cluster_end = cluster_end.max(c.fix.end as i64);
            cluster.push(c);
        }
    }
    flush_cluster(&mut cluster, &mut applied, &mut skipped);
    (applied, skipped)
}

fn flush_cluster(
    cluster: &mut Vec<Candidate>,
    applied: &mut Vec<Candidate>,
    skipped: &mut Vec<FixSkip>,
) {
    if cluster.is_empty() {
        return;
    }
    let winner_idx = cluster
        .iter()
        .enumerate()
        .min_by_key(|(_, c)| {
            (
                if c.fix.confidence == FixConfidence::Safe {
                    0u8
                } else {
                    1u8
                },
                c.rule_id.clone(),
                c.fix.start,
                c.fix.end,
            )
        })
        .map(|(i, _)| i)
        .expect("cluster is non-empty");
    for (i, c) in cluster.drain(..).enumerate() {
        if i == winner_idx {
            applied.push(c);
        } else {
            skipped.push(FixSkip {
                file: c.file.clone(),
                fix: c.fix.clone(),
                rule_id: c.rule_id.clone(),
                reason: SkipReason::Conflict,
            });
        }
    }
}

/// Apply `fixes` to `source_chars` in reverse-position order so
/// earlier offsets are not shifted by later edits. Positions are
/// Unicode codepoint offsets (see `report::Fix`'s doc comment) —
/// `source_chars` must be the same codepoint-indexed representation
/// the fixes' offsets were computed against. Mirrors
/// `fixer.py::_apply_to_text`; that function's own doc comment claims
/// pylatexenc positions are byte offsets, but Python `str` slicing is
/// always codepoint-based regardless of what pylatexenc calls it —
/// already corrected project-wide (see `report::Fix`'s doc comment).
pub fn apply_to_text(source_chars: &[char], fixes: &[Candidate]) -> String {
    let mut ordered: Vec<&Candidate> = fixes.iter().collect();
    ordered.sort_by_key(|c| std::cmp::Reverse(c.fix.start));
    let mut chars: Vec<char> = source_chars.to_vec();
    for c in ordered {
        let mut next = chars[..c.fix.start].to_vec();
        next.extend(c.fix.replacement.chars());
        next.extend(&chars[c.fix.end..]);
        chars = next;
    }
    chars.into_iter().collect()
}
