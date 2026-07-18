//! Terminal renderer — mirrors `output/terminal.py`'s `rich`-based
//! rendering for the NON-terminal (piped/redirected stdout) case,
//! which is what `Console(force_terminal=False, ...)` produces when
//! `sys.stdout` isn't a real tty (the overwhelmingly common case: CI,
//! editor-integration subprocess calls, `> file.txt`). No ANSI color
//! codes are emitted in that case even though the Python source
//! builds `[red]...[/red]`-style markup — `rich` strips it down to
//! plain text automatically. Real-terminal (tty) colored output is
//! NOT replicated here; this module only targets the non-tty path.
//!
//! Faithfully replicates one genuine `rich` quirk rather than working
//! around it: `Table.add_row(str)` parses EVERY string cell as rich
//! markup, so any `[lowercase...]` bracket run in a violation message
//! or suggestion — e.g. `\citep[e.g.][]{key}` — gets silently
//! swallowed (rich attempts to interpret `[e.g.]` as a style tag,
//! fails to find a `e.g.`-named style, and drops it, changing the
//! rendered text to `\citep[]{key}`). Confirmed empirically against
//! the real Python renderer; see `strip_markup`'s doc comment.

use crate::catalogue;
use crate::config::{Mode, ToolConfig};
use crate::report::{ComplianceReport, Violation};
use regex::Regex;
use std::sync::LazyLock;

const CONSOLE_WIDTH: usize = 120;

// ---------------------------------------------------------------------
// Markup stripping — mirrors rich.markup's tag regex and substitution.
// ---------------------------------------------------------------------

/// Mirrors `rich.markup.RE_TAGS = re.compile(r"((\\*)\[([a-z#/@][^[]*?)])")`.
static TAG_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(\\*)\[([a-z#/@][^\[]*?)\]").unwrap());

/// Strips every `[tag]`-shaped bracket run (content starting with a
/// lowercase letter, `#`, `/`, or `@`) the way `rich.markup.render`
/// does: the tag itself (brackets + content) is removed entirely,
/// regardless of whether the "style name" is real — `rich` doesn't
/// validate until render time, and non-tty rendering never needs a
/// real `Style`, so an invalid tag is silently absorbed just like a
/// valid one. `\[` (single backslash before `[`) is the one escape
/// `rich` recognizes and unescapes to a literal `[`; runs of 2+
/// backslashes aren't precisely replicated (not observed in any real
/// JSS rule message/suggestion).
pub fn strip_markup(s: &str) -> String {
    if !s.contains('[') {
        return s.to_string();
    }
    let mut out = String::new();
    let mut last_end = 0;
    for caps in TAG_RE.captures_iter(s) {
        let whole = caps.get(0).unwrap();
        let backslashes = caps.get(1).unwrap().as_str();
        let pre = &s[last_end..whole.start()];
        out.push_str(&pre.replace("\\[", "["));
        if backslashes.chars().count() % 2 == 1 {
            // Escaped: not a real tag. Keep one fewer backslash (the
            // one that did the escaping) plus the literal brackets.
            let kept = &backslashes[..backslashes.len() - 1];
            out.push_str(kept);
            out.push('[');
            out.push_str(caps.get(2).unwrap().as_str());
            out.push(']');
        }
        // else: a real tag — contributes nothing to plain text.
        last_end = whole.end();
    }
    out.push_str(&s[last_end..].replace("\\[", "["));
    out
}

// ---------------------------------------------------------------------
// console.rule() — mirrors rich.rule.Rule.__rich_console__ (align="center").
// ---------------------------------------------------------------------

fn truncate_ellipsis(s: &str, max_width: usize) -> String {
    let len = s.chars().count();
    if len <= max_width {
        return s.to_string();
    }
    if max_width == 0 {
        return String::new();
    }
    let kept: String = s.chars().take(max_width - 1).collect();
    format!("{kept}…")
}

/// Mirrors `Rule.__rich_console__` with `align="center"`,
/// `characters="─"`. Rich's own arithmetic overshoots the target
/// width by exactly 2 (a quirk of how `left`/`right` are each
/// independently sized), which the generic console render pipeline
/// then crops back down to `width` — replicated here as "build, then
/// crop/pad to exactly `width`" rather than chasing the intermediate
/// off-by-two.
fn rule_line(title: &str, width: usize) -> String {
    if title.is_empty() {
        return "─".repeat(width);
    }
    let title = title.replace('\n', " ");
    let required_space = 4;
    let truncate_width = width.saturating_sub(required_space);
    if truncate_width == 0 {
        return "─".repeat(width);
    }
    let title = truncate_ellipsis(&title, truncate_width);
    let title_len = title.chars().count();
    let side_width = width.saturating_sub(title_len) / 2;
    let left_len = side_width.saturating_sub(1);
    let left = "─".repeat(left_len);
    let right_length = width.saturating_sub(left_len).saturating_sub(title_len);
    let right = "─".repeat(right_length);
    let mut line = format!("{left} {title} {right}");
    let chars: Vec<char> = line.chars().collect();
    if chars.len() > width {
        line = chars[..width].iter().collect();
    } else if chars.len() < width {
        line.push_str(&" ".repeat(width - chars.len()));
    }
    line
}

// ---------------------------------------------------------------------
// Cell measurement + word-wrap — mirrors rich.text.Text.__rich_measure__
// and rich._wrap.divide_line.
// ---------------------------------------------------------------------

/// `(min_width, max_width)`: min = longest single word (so wrapping
/// never breaks a word unnecessarily), max = longest line (content
/// may already contain embedded `\n`, e.g. the confidence suffix).
fn measure_cell(text: &str) -> (usize, usize) {
    let lines: Vec<&str> = if text.is_empty() {
        vec![""]
    } else {
        text.split('\n').collect()
    };
    let max_width = lines.iter().map(|l| l.chars().count()).max().unwrap_or(0);
    let words: Vec<&str> = text.split_whitespace().collect();
    let min_width = if words.is_empty() {
        max_width
    } else {
        words.iter().map(|w| w.chars().count()).max().unwrap()
    };
    (min_width, max_width)
}

/// `(start, word)` pairs mirroring `rich._wrap.words`: each "word"
/// includes its trailing whitespace run (not its leading one — that
/// was consumed by the previous word).
fn words(text: &[char]) -> Vec<(usize, String)> {
    let n = text.len();
    let mut out = Vec::new();
    let mut pos = 0;
    while pos < n {
        let start = pos;
        let mut i = pos;
        while i < n && text[i].is_whitespace() {
            i += 1;
        }
        if i >= n {
            break;
        }
        while i < n && !text[i].is_whitespace() {
            i += 1;
        }
        while i < n && text[i].is_whitespace() {
            i += 1;
        }
        out.push((start, text[start..i].iter().collect::<String>()));
        pos = i;
    }
    out
}

/// Break offsets (codepoint indices) mirroring `rich._wrap.divide_line`
/// with `fold=False` — the actual mode `Text.wrap` uses for our
/// columns, since `wrap_overflow` defaults to `"ellipsis"`, not
/// `"fold"` (`fold=(wrap_overflow == "fold")` in `Text.wrap`). A word
/// longer than `width` is NOT hard-broken here: it's isolated onto
/// its own line (a break is inserted before it, if there was
/// preceding content), and `Text.wrap` separately truncates every
/// resulting line to `width` with an ellipsis afterward — see
/// `wrap_single_line`.
fn divide_line(text: &str, width: usize) -> Vec<usize> {
    let chars: Vec<char> = text.chars().collect();
    let mut breaks = Vec::new();
    let mut cell_offset: i64 = 0;
    for (start, word) in words(&chars) {
        let word_chars: Vec<char> = word.chars().collect();
        let word_len = word.trim_end().chars().count() as i64;
        let remaining = width as i64 - cell_offset;
        if remaining >= word_len {
            cell_offset += word_chars.len() as i64;
        } else if word_len > width as i64 {
            if start > 0 {
                breaks.push(start);
            }
            cell_offset = word_len;
        } else if cell_offset > 0 && start > 0 {
            breaks.push(start);
            cell_offset = word_chars.len() as i64;
        }
    }
    breaks
}

fn wrap_single_line(text: &str, width: usize) -> Vec<String> {
    if width == 0 {
        return vec![text.to_string()];
    }
    let breaks = divide_line(text, width);
    let chars: Vec<char> = text.chars().collect();
    let mut lines = Vec::new();
    let mut start = 0;
    for &b in &breaks {
        lines.push(chars[start..b].iter().collect::<String>());
        start = b;
    }
    lines.push(chars[start..].iter().collect::<String>());
    // Mirrors `Text.wrap`'s post-processing: rstrip each raw wrapped
    // line (the word-boundary trailing space `divide_line` carries
    // along), then truncate-with-ellipsis to `width` — a no-op for
    // every line that already fits; only a line isolating a single
    // word longer than `width` (see `divide_line`'s doc comment)
    // actually gets shortened here.
    lines
        .into_iter()
        .map(|l| truncate_ellipsis(l.trim_end(), width))
        .collect()
}

/// Wraps `text` (which may already contain embedded `\n`, e.g. the
/// confidence-tier suffix) into lines fitting `width` cells each.
fn wrap_cell(text: &str, width: usize) -> Vec<String> {
    let mut out = Vec::new();
    for segment in text.split('\n') {
        out.extend(wrap_single_line(segment, width));
    }
    if out.is_empty() {
        out.push(String::new());
    }
    out
}

// ---------------------------------------------------------------------
// Table rendering — mirrors rich.table.Table (box.HEAVY_HEAD,
// padding=(0,1), pad_edge=True, expand=False, show_lines=False).
// ---------------------------------------------------------------------

struct Column {
    header: &'static str,
    no_wrap: bool,
    right_justify: bool,
}

fn col(header: &'static str) -> Column {
    Column {
        header,
        no_wrap: false,
        right_justify: false,
    }
}

fn col_no_wrap(header: &'static str) -> Column {
    Column {
        header,
        no_wrap: true,
        right_justify: false,
    }
}

fn col_right(header: &'static str) -> Column {
    Column {
        header,
        no_wrap: false,
        right_justify: true,
    }
}

/// Mirrors `Table._calculate_column_widths` (the `expand=False` path:
/// natural per-column width, collapsed via `_collapse_widths` only
/// when the natural total exceeds the console width; the "pad to
/// fill" branch never applies since none of these tables set
/// `expand=True`). Returns border-inclusive-padding widths (content +
/// 2 for the 1-space-each-side default padding).
fn column_widths(columns: &[Column], rows: &[Vec<String>], total_width: usize) -> Vec<usize> {
    let ncols = columns.len();
    let mut max_w = vec![0usize; ncols];
    for (i, c) in columns.iter().enumerate() {
        max_w[i] = measure_cell(c.header).1;
    }
    for row in rows {
        for (i, cell) in row.iter().enumerate() {
            max_w[i] = max_w[i].max(measure_cell(cell).1);
        }
    }
    let mut widths: Vec<usize> = max_w.iter().map(|w| w + 2).collect();
    let borders = ncols + 1;
    let budget = total_width.saturating_sub(borders);
    let table_content_width: usize = widths.iter().sum();
    if table_content_width > budget {
        let wrapable: Vec<bool> = columns.iter().map(|c| !c.no_wrap).collect();
        widths = collapse_widths(widths, &wrapable, budget);
    }
    widths
}

/// Mirrors `Table._collapse_widths`: repeatedly reduce the currently
/// widest wrapable column(s) down toward the second-widest, until the
/// total fits (or no further reduction is possible).
fn collapse_widths(mut widths: Vec<usize>, wrapable: &[bool], max_width: usize) -> Vec<usize> {
    let total: usize = widths.iter().sum();
    if total <= max_width || !wrapable.iter().any(|&w| w) {
        return widths;
    }
    let mut excess = total as i64 - max_width as i64;
    loop {
        if excess <= 0 {
            break;
        }
        let max_col = widths
            .iter()
            .zip(wrapable)
            .filter(|(_, &w)| w)
            .map(|(&w, _)| w)
            .max();
        let Some(max_col) = max_col else { break };
        let second_max = widths
            .iter()
            .zip(wrapable)
            .map(|(&w, &allow)| if allow && w != max_col { w } else { 0 })
            .max()
            .unwrap_or(0);
        let column_difference = max_col as i64 - second_max as i64;
        if column_difference == 0 {
            break;
        }
        let max_reduce = excess.min(column_difference);
        // ratio_reduce with ratio 1 on every column tied for max_col
        // (equal split of `excess`, capped at `max_reduce` each).
        let candidates: Vec<usize> = widths
            .iter()
            .zip(wrapable)
            .enumerate()
            .filter(|(_, (&w, &allow))| allow && w == max_col)
            .map(|(i, _)| i)
            .collect();
        if candidates.is_empty() {
            break;
        }
        let mut remaining = excess;
        let mut total_ratio = candidates.len() as i64;
        for &i in &candidates {
            // Python's `round()` on a float is round-half-to-even, not
            // `f64::round()`'s round-half-away-from-zero — an exact
            // `.5` tie here is a realistic occurrence (small integer
            // ratios), not a hypothetical edge case; ported this way
            // once already in `conformance.rs::python_round_to_i64`.
            let distributed =
                max_reduce.min((remaining as f64 / total_ratio as f64).round_ties_even() as i64);
            widths[i] = (widths[i] as i64 - distributed).max(0) as usize;
            remaining -= distributed;
            total_ratio -= 1;
        }
        let new_total: usize = widths.iter().sum();
        excess = new_total as i64 - max_width as i64;
    }
    widths
}

fn justify(text: &str, width: usize, right: bool) -> String {
    let len = text.chars().count();
    if len >= width {
        return text.to_string();
    }
    let pad = width - len;
    if right {
        format!("{}{}", " ".repeat(pad), text)
    } else {
        format!("{}{}", text, " ".repeat(pad))
    }
}

/// Renders one complete `rich.table.Table` (box.HEAVY_HEAD, header +
/// body, no footer, no row separators) as it appears on a non-tty
/// console. `rows` are already-stripped-of-markup plain strings.
fn render_table(columns: &[Column], rows: &[Vec<String>], title: Option<&str>) -> String {
    let widths = column_widths(columns, rows, CONSOLE_WIDTH);
    let table_width: usize = widths.iter().sum::<usize>() + columns.len() + 1;

    let mut out = String::new();
    if let Some(t) = title {
        out.push_str(&center_text(t, table_width));
        out.push('\n');
    }

    // Top border.
    out.push('┏');
    for (i, &w) in widths.iter().enumerate() {
        out.push_str(&"━".repeat(w));
        out.push(if i + 1 < widths.len() { '┳' } else { '┓' });
    }
    out.push('\n');

    // Header row.
    out.push('┃');
    for (i, c) in columns.iter().enumerate() {
        out.push(' ');
        out.push_str(&justify(c.header, widths[i] - 2, false));
        out.push(' ');
        out.push('┃');
    }
    out.push('\n');

    // Header/body separator.
    out.push('┡');
    for (i, &w) in widths.iter().enumerate() {
        out.push_str(&"━".repeat(w));
        out.push(if i + 1 < widths.len() { '╇' } else { '┩' });
    }
    out.push('\n');

    // Body rows.
    for row in rows {
        let wrapped: Vec<Vec<String>> = row
            .iter()
            .enumerate()
            .map(|(i, cell)| wrap_cell(cell, widths[i] - 2))
            .collect();
        let height = wrapped.iter().map(|l| l.len()).max().unwrap_or(1);
        for line_idx in 0..height {
            out.push('│');
            for (i, c) in columns.iter().enumerate() {
                let content = wrapped[i].get(line_idx).map(String::as_str).unwrap_or("");
                out.push(' ');
                out.push_str(&justify(content, widths[i] - 2, c.right_justify));
                out.push(' ');
                out.push('│');
            }
            out.push('\n');
        }
    }

    // Bottom border.
    out.push('└');
    for (i, &w) in widths.iter().enumerate() {
        out.push_str(&"─".repeat(w));
        out.push(if i + 1 < widths.len() { '┴' } else { '┘' });
    }
    out.push('\n');

    out
}

fn center_text(text: &str, width: usize) -> String {
    let len = text.chars().count();
    if len >= width {
        return text.to_string();
    }
    let total_pad = width - len;
    let left = total_pad / 2;
    let right = total_pad - left;
    format!("{}{}{}", " ".repeat(left), text, " ".repeat(right))
}

// ---------------------------------------------------------------------
// Suffix helpers — mirrors terminal.py's _guide_suffix/_confidence_suffix.
// ---------------------------------------------------------------------

fn guide_suffix(rule_id: &str) -> String {
    let Some(meta) = catalogue::lookup(rule_id) else {
        return String::new();
    };
    let section = meta.guide_section;
    if section.is_empty() || section == "internal" {
        return String::new();
    }
    format!(" (see {section})")
}

fn confidence_suffix(rule_id: &str) -> String {
    let Some(meta) = catalogue::lookup(rule_id) else {
        return String::new();
    };
    if meta.confidence == "high" {
        return String::new();
    }
    format!("\n({} conf.)", meta.confidence)
}

fn display_path(raw: &str) -> String {
    let Ok(cwd) = std::env::current_dir() else {
        return raw.to_string();
    };
    let path = std::path::Path::new(raw);
    let Ok(resolved) = std::fs::canonicalize(path).or_else(|_| {
        // canonicalize requires the path to exist; fall back to a
        // lexical join against cwd for a path that may not (matches
        // Python's Path.resolve(), which doesn't require existence).
        Ok::<_, std::io::Error>(if path.is_absolute() {
            path.to_path_buf()
        } else {
            cwd.join(path)
        })
    }) else {
        return raw.to_string();
    };
    match resolved.strip_prefix(&cwd) {
        Ok(rel) => rel.to_string_lossy().to_string(),
        Err(_) => raw.to_string(),
    }
}

// ---------------------------------------------------------------------
// Top-level render — mirrors terminal.py::render.
// ---------------------------------------------------------------------

pub fn render(report: &ComplianceReport, config: &ToolConfig) -> String {
    let mut out = String::new();
    if config.mode == Mode::Reviewer {
        render_reviewer(report, &mut out);
    } else {
        render_author(report, &mut out);
    }
    if config.verbose && !report.skipped_rules.is_empty() {
        render_skipped_rules(report, &mut out);
    }
    out
}

fn render_author(report: &ComplianceReport, out: &mut String) {
    let mut files: Vec<&str> = report.violations.iter().map(|v| v.file.as_str()).collect();
    files.sort();
    files.dedup();
    if files.is_empty() {
        return;
    }

    let columns = [
        col_no_wrap("Line:Col"),
        col_no_wrap("Severity"),
        col_no_wrap("Rule"),
        col("Message"),
        col("Suggestion"),
    ];

    for file in files {
        out.push_str(&rule_line(&display_path(file), CONSOLE_WIDTH));
        out.push('\n');
        let file_violations: Vec<&Violation> = report
            .violations
            .iter()
            .filter(|v| v.file == file)
            .collect();
        let rows: Vec<Vec<String>> = file_violations
            .iter()
            .map(|v| {
                let locator = match v.column {
                    Some(c) => format!("{}:{c}", v.line),
                    None => v.line.to_string(),
                };
                let rule_cell =
                    strip_markup(&format!("{}{}", v.rule_id, confidence_suffix(&v.rule_id)));
                let message_cell =
                    strip_markup(&format!("{}{}", v.message, guide_suffix(&v.rule_id)));
                let suggestion_cell = strip_markup(v.suggestion.as_deref().unwrap_or(""));
                vec![
                    locator,
                    v.severity.as_str().to_string(),
                    rule_cell,
                    message_cell,
                    suggestion_cell,
                ]
            })
            .collect();
        out.push_str(&render_table(&columns, &rows, None));
    }
}

fn render_reviewer(report: &ComplianceReport, out: &mut String) {
    let columns = [
        col_no_wrap("Category"),
        col_no_wrap("Status"),
        col_right("Applied"),
        col_right("Passed"),
    ];
    let rows: Vec<Vec<String>> = report
        .categories
        .iter()
        .map(|c| {
            vec![
                c.title.clone(),
                c.status.as_str().to_string(),
                c.rules_applied.to_string(),
                c.rules_passed.to_string(),
            ]
        })
        .collect();
    let title = format!("Journal compliance — {}", report.journal_id);
    out.push_str(&render_table(&columns, &rows, Some(&title)));
    match report.compliance_percentage {
        // Python's `f"{pct}%"` formats a `round(x, 1)` float, which
        // Python always shows with at least one decimal digit (40.0,
        // not 40) — Rust's f64 Display drops a trailing ".0".
        Some(pct) => out.push_str(&format!("Overall: {pct:.1}%\n")),
        None => out.push_str("Overall: n/a\n"),
    }
}

fn render_skipped_rules(report: &ComplianceReport, out: &mut String) {
    out.push_str(&rule_line("Skipped rules", CONSOLE_WIDTH));
    out.push('\n');
    let columns = [col_no_wrap("Rule"), col("Reason")];
    let rows: Vec<Vec<String>> = report
        .skipped_rules
        .iter()
        .map(|s| vec![s.rule_id.clone(), strip_markup(&s.reason)])
        .collect();
    out.push_str(&render_table(&columns, &rows, None));
}
