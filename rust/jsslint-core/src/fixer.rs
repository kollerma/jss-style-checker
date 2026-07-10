//! Auto-fix engine — mirrors `core/fixer.py` in full, including the
//! file I/O, atomic write, interactive prompting, and
//! re-validation-by-re-running-the-whole-engine parts of Python's
//! `apply_fixes` (deferred in the initial port to a pure-logic subset
//! since a fully assembled rule engine didn't exist yet; Phase 4 now
//! has one).

use crate::config::ToolConfig;
use crate::engine::{self, ParsedDocument};
use crate::report::{ComplianceReport, Fix, FixConfidence, Violation};
use std::collections::HashSet;
use std::io::{BufRead, Write};
use std::path::Path;

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

/// Mirrors `fixer.py::ApplyMode`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ApplyMode {
    Write,
    DryRun,
    Interactive,
}

/// Mirrors `fixer.py::FixApplication`.
#[derive(Debug, Clone)]
pub struct FixApplication {
    pub file: String,
    pub fix: Fix,
    pub rule_id: String,
}

/// Mirrors `fixer.py::RejectReason`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RejectReason {
    Regression,
    PermissionDenied,
}

/// Mirrors `fixer.py::FixRejection`.
#[derive(Debug, Clone)]
pub struct FixRejection {
    pub file: String,
    pub fix: Fix,
    pub rule_id: String,
    pub reason: RejectReason,
}

/// Mirrors `fixer.py::FixReport`.
#[derive(Debug, Clone, Default)]
pub struct FixReport {
    pub applied: Vec<FixApplication>,
    pub skipped: Vec<FixSkip>,
    pub rejected: Vec<FixRejection>,
}

/// Splits `text` the way Python's `str.splitlines(keepends=True)` does
/// for the line endings real manuscripts actually use (`\n`, `\r\n`,
/// bare `\r`) — deliberately not the full Unicode line-boundary table
/// (`\v`, `\f`, `\x1c`-`\x1e`, `\x85`, U+2028/U+2029), none of which
/// appear in the fixture/recall corpus.
fn splitlines_keepends(text: &str) -> Vec<String> {
    let mut lines = Vec::new();
    let mut line_start = 0usize;
    let mut chars = text.char_indices().peekable();
    while let Some((i, c)) = chars.next() {
        if c == '\n' {
            lines.push(text[line_start..i + 1].to_string());
            line_start = i + 1;
        } else if c == '\r' {
            if let Some(&(j, '\n')) = chars.peek() {
                chars.next();
                lines.push(text[line_start..j + 1].to_string());
                line_start = j + 1;
            } else {
                lines.push(text[line_start..i + 1].to_string());
                line_start = i + 1;
            }
        }
    }
    if line_start < text.len() {
        lines.push(text[line_start..].to_string());
    }
    lines
}

/// Mirrors `difflib.py::_format_range_unified` — not exported by the
/// `difflib` crate (its `utils` module is private), so reimplemented
/// here; it's five lines.
fn format_range_unified(start: usize, end: usize) -> String {
    let mut beginning = start + 1;
    let length = end - start;
    if length == 1 {
        return beginning.to_string();
    }
    if length == 0 {
        beginning -= 1;
    }
    format!("{beginning},{length}")
}

/// Mirrors `fixer.py::_unified_diff` (`difflib.unified_diff`, default
/// `n=3` context, no `fromfiledate`/`tofiledate`). Built directly on
/// the `difflib` crate's `SequenceMatcher` (a byte-for-byte port of
/// Python's, including the `len(b) >= 200` popular-element / autojunk
/// filtering) rather than the crate's own `unified_diff()` helper,
/// which unconditionally appends a `\t` header suffix even when
/// `from_file_date`/`to_file_date` are empty — Python's
/// `difflib.unified_diff` only adds that `\t` when a date is actually
/// given (`'\t{}'.format(fromfiledate) if fromfiledate else ''`).
fn unified_diff_text(file: &str, before: &str, after: &str) -> String {
    let before_lines = splitlines_keepends(before);
    let after_lines = splitlines_keepends(after);
    let mut matcher = difflib::sequencematcher::SequenceMatcher::new(&before_lines, &after_lines);
    let mut out = String::new();
    let mut started = false;
    for group in matcher.get_grouped_opcodes(3) {
        if !started {
            started = true;
            out.push_str(&format!("--- {file}\n"));
            out.push_str(&format!("+++ {file}\n"));
        }
        let first = group.first().expect("grouped opcodes are non-empty");
        let last = group.last().expect("grouped opcodes are non-empty");
        let file1_range = format_range_unified(first.first_start, last.first_end);
        let file2_range = format_range_unified(first.second_start, last.second_end);
        out.push_str(&format!("@@ -{file1_range} +{file2_range} @@\n"));
        for code in &group {
            if code.tag == "equal" {
                for item in &before_lines[code.first_start..code.first_end] {
                    out.push(' ');
                    out.push_str(item);
                }
                continue;
            }
            if code.tag == "replace" || code.tag == "delete" {
                for item in &before_lines[code.first_start..code.first_end] {
                    out.push('-');
                    out.push_str(item);
                }
            }
            if code.tag == "replace" || code.tag == "insert" {
                for item in &after_lines[code.second_start..code.second_end] {
                    out.push('+');
                    out.push_str(item);
                }
            }
        }
    }
    out
}

/// Tempfile + rename, mirroring `fixer.py::_atomic_write`'s
/// `tempfile.mkstemp` + `os.replace` (POSIX rename is atomic; exact
/// temp-file naming isn't part of the observable contract, only that
/// the target is never left partially written).
fn atomic_write(target: &Path, contents: &[u8]) -> std::io::Result<()> {
    let parent = target.parent().unwrap_or_else(|| Path::new("."));
    let file_name = target
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let tmp_path = parent.join(format!(
        ".jss-lint.{}.{}.tmp",
        std::process::id(),
        file_name
    ));
    {
        let mut f = std::fs::File::create(&tmp_path)?;
        f.write_all(contents)?;
        f.flush()?;
        let _ = f.sync_all();
    }
    std::fs::rename(&tmp_path, target)?;
    Ok(())
}

/// Re-parses + re-lints `target` and returns `true` iff none of the
/// `(rule_id, line)` pairs in `before` re-appear. Mirrors
/// `fixer.py::_re_validate`, using `ToolConfig::default()` rather than
/// re-loading a per-directory `.jss-lint.toml` — config-file loading
/// isn't ported yet (task: "Port .jss-lint.toml config-file loading"),
/// and `load_config({}, ...)` with no such file present resolves to
/// the same defaults Python would use today.
fn re_validate(target: &Path, before: &HashSet<(String, u32)>) -> bool {
    let Ok(contents) = std::fs::read_to_string(target) else {
        return true;
    };
    let sources = vec![(target.to_string_lossy().into_owned(), contents)];
    let Ok(document) = ParsedDocument::from_sources(&sources) else {
        return true;
    };
    let cfg = ToolConfig::default();
    let report = engine::run(&cfg, &document);
    let after: HashSet<(String, u32)> = report
        .violations
        .iter()
        .map(|v| (v.rule_id.clone(), v.line))
        .collect();
    before.is_disjoint(&after)
}

/// Apply auto-fixes from `report` per spec 008. Mirrors
/// `fixer.py::apply_fixes`.
#[allow(clippy::too_many_arguments)]
pub fn apply_fixes(
    report: &ComplianceReport,
    mode: ApplyMode,
    rules: Option<&HashSet<String>>,
    stdin: &mut dyn BufRead,
    stdout: &mut dyn Write,
    stderr: &mut dyn Write,
) -> FixReport {
    let all_candidates = candidates_from_violations(&report.violations);
    let mut skipped_all: Vec<FixSkip> = Vec::new();
    let candidates: Vec<Candidate> = if let Some(rules) = rules {
        let (keep, drop): (Vec<Candidate>, Vec<Candidate>) = all_candidates
            .into_iter()
            .partition(|c| rules.contains(&c.rule_id));
        skipped_all.extend(drop.into_iter().map(|c| FixSkip {
            file: c.file,
            fix: c.fix,
            rule_id: c.rule_id,
            reason: SkipReason::RuleNotSelected,
        }));
        keep
    } else {
        all_candidates
    };

    let mut by_file: std::collections::BTreeMap<String, Vec<Candidate>> =
        std::collections::BTreeMap::new();
    for c in candidates {
        by_file.entry(c.file.clone()).or_default().push(c);
    }

    let mut applied_all: Vec<FixApplication> = Vec::new();
    let mut rejected_all: Vec<FixRejection> = Vec::new();

    for (file, fixes) in by_file {
        let path = Path::new(&file);
        let (per_file_applied, per_file_skipped) = resolve_conflicts(fixes);
        skipped_all.extend(per_file_skipped);

        if per_file_applied.is_empty() {
            continue;
        }

        let before = match std::fs::read_to_string(path) {
            Ok(b) => b,
            Err(exc) => {
                rejected_all.extend(per_file_applied.iter().map(|c| FixRejection {
                    file: c.file.clone(),
                    fix: c.fix.clone(),
                    rule_id: c.rule_id.clone(),
                    reason: RejectReason::PermissionDenied,
                }));
                let _ = writeln!(stderr, "jss-lint: {file}: {exc}");
                continue;
            }
        };

        let mut accepted: Vec<Candidate> = Vec::new();
        if mode == ApplyMode::Interactive {
            let mut idx = 0usize;
            while idx < per_file_applied.len() {
                let c = &per_file_applied[idx];
                let before_chars: Vec<char> = before.chars().collect();
                let single_after = apply_to_text(&before_chars, std::slice::from_ref(c));
                let hunk = unified_diff_text(&file, &before, &single_after);
                let _ = write!(stdout, "{hunk}");
                let _ = write!(
                    stdout,
                    "Apply fix for {} at line {}? [y/n/a/q] ",
                    c.rule_id, c.line
                );
                let _ = stdout.flush();
                let mut reply = String::new();
                let read = stdin.read_line(&mut reply);
                let reply = match read {
                    Ok(0) | Err(_) => "q".to_string(),
                    Ok(_) => reply,
                };
                match reply.trim().to_lowercase().as_str() {
                    "y" => {
                        accepted.push(per_file_applied[idx].clone());
                        idx += 1;
                    }
                    "a" => {
                        accepted.extend(per_file_applied[idx..].iter().cloned());
                        break;
                    }
                    "q" => {
                        skipped_all.extend(per_file_applied[idx..].iter().map(|x| FixSkip {
                            file: x.file.clone(),
                            fix: x.fix.clone(),
                            rule_id: x.rule_id.clone(),
                            reason: SkipReason::UserSkipped,
                        }));
                        break;
                    }
                    _ => {
                        skipped_all.push(FixSkip {
                            file: c.file.clone(),
                            fix: c.fix.clone(),
                            rule_id: c.rule_id.clone(),
                            reason: SkipReason::UserSkipped,
                        });
                        idx += 1;
                    }
                }
            }
        } else {
            accepted = per_file_applied;
        }

        if accepted.is_empty() {
            continue;
        }

        let before_chars: Vec<char> = before.chars().collect();
        let after = apply_to_text(&before_chars, &accepted);

        if mode == ApplyMode::DryRun {
            let _ = write!(stdout, "{}", unified_diff_text(&file, &before, &after));
            applied_all.extend(accepted.iter().map(|c| FixApplication {
                file: c.file.clone(),
                fix: c.fix.clone(),
                rule_id: c.rule_id.clone(),
            }));
            continue;
        }

        if let Err(exc) = atomic_write(path, after.as_bytes()) {
            rejected_all.extend(accepted.iter().map(|c| FixRejection {
                file: c.file.clone(),
                fix: c.fix.clone(),
                rule_id: c.rule_id.clone(),
                reason: RejectReason::PermissionDenied,
            }));
            let _ = writeln!(stderr, "jss-lint: {file}: {exc}");
            continue;
        }

        let rule_id_lines_before: HashSet<(String, u32)> = accepted
            .iter()
            .map(|c| (c.rule_id.clone(), c.line))
            .collect();
        if !re_validate(path, &rule_id_lines_before) {
            let _ = atomic_write(path, before.as_bytes());
            rejected_all.extend(accepted.iter().map(|c| FixRejection {
                file: c.file.clone(),
                fix: c.fix.clone(),
                rule_id: c.rule_id.clone(),
                reason: RejectReason::Regression,
            }));
            for c in &accepted {
                let _ = writeln!(
                    stderr,
                    "jss-lint: {} fix rejected (regression on rewrite); file rolled back: {}",
                    c.rule_id, file
                );
            }
            continue;
        }

        applied_all.extend(accepted.iter().map(|c| FixApplication {
            file: c.file.clone(),
            fix: c.fix.clone(),
            rule_id: c.rule_id.clone(),
        }));
    }

    FixReport {
        applied: applied_all,
        skipped: skipped_all,
        rejected: rejected_all,
    }
}
