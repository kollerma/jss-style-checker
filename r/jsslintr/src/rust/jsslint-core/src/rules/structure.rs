//! Structure rules — mirrors `journals/jss/rules/structure.py`
//! (JSS-STRUCT-001..006).

use super::tex_common::{lineno_col, make_violation, tex_violation_with_fix};
use crate::report::{Fix, FixConfidence, Violation};
use crate::tex::extract;
use crate::tex::node::{GroupNode, MacroNode, Node};
use crate::tex::prose::{walk, Slot};
use crate::tex::{position::LineIndex, ParsedTex};
use regex::Regex;
use std::sync::LazyLock;

static SUMMARY_WORDS_RE: LazyLock<Regex> = LazyLock::new(|| {
    regex_ignore_case(
        r"\b(summary|discussion|conclusion|conclusions|concluding|illustrations?|examples?|applications?|outlook)\b",
    )
});
static BACKMATTER_TITLE_RE: LazyLock<Regex> = LazyLock::new(|| {
    regex_ignore_case(
        r"^\s*(acknowledg|funding?|session\s*info|computational\s*details|appendix|appendices|references|notation|glossar|nomenclature|list\s+of\s+(?:symbols|figures|tables)|code\s+for\s+section|derivation\s+of|proof\s+of|proofs)",
    )
});
const PAGEBREAK_MACROS: &[&str] = &["newpage", "clearpage", "cleardoublepage", "pagebreak"];
const STRUCT_SECTION_MACROS: &[&str] = &[
    "section",
    "section*",
    "subsection",
    "subsection*",
    "chapter",
    "chapter*",
];
const TOP_LEVEL_SECTION_MACROS: &[&str] = &["section", "section*", "chapter", "chapter*"];

fn regex_ignore_case(pattern: &str) -> Regex {
    regex::RegexBuilder::new(pattern)
        .case_insensitive(true)
        .build()
        .unwrap()
}

fn first_arg_text<'a>(macro_node: &'a MacroNode, parent: &[Slot<'a>], idx: usize) -> String {
    extract::macro_args_text(macro_node, parent, idx)
}

/// JSS-STRUCT-001 — document ends with a summary/discussion section
/// before the bibliography.
pub fn check_struct_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    let Some(bib_pos) = find_bibliography_pos(&parsed.nodes) else {
        return out;
    };

    let mut sections: Vec<(&MacroNode, String)> = Vec::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent: &[Slot], idx, node| {
        if node.span().pos >= bib_pos {
            return;
        }
        let Node::Macro(m) = node else { return };
        if !TOP_LEVEL_SECTION_MACROS.contains(&m.macroname.as_str()) {
            return;
        }
        sections.push((m, first_arg_text(m, parent, idx)));
    });

    let last_content = sections
        .iter()
        .rev()
        .find(|(_, title)| !BACKMATTER_TITLE_RE.is_match(title));
    let Some((node, title)) = last_content else {
        return out;
    };
    if SUMMARY_WORDS_RE.is_match(title) {
        return out;
    }
    out.push(tex_violation_with_fix(
        file,
        &line_index,
        node.span.pos,
        "JSS-STRUCT-001",
        Some(
            "Add a 'Summary and discussion' (or similar) section before the bibliography."
                .to_string(),
        ),
        None,
    ));
    out
}

fn find_bibliography_pos(nodes: &[Node]) -> Option<usize> {
    let mut found = None;
    walk(nodes, &mut |node, _ancestors| {
        if found.is_some() {
            return;
        }
        match node {
            Node::Macro(m) if m.macroname == "bibliography" => found = Some(m.span.pos),
            Node::Environment(e) if e.environmentname == "thebibliography" => {
                found = Some(e.span.pos)
            }
            _ => {}
        }
    });
    found
}

// --- JSS-STRUCT-002 -------------------------------------------------------

static ACKNOWLEDGEMENT_WORD_RE: LazyLock<Regex> =
    LazyLock::new(|| regex_ignore_case(r"\backnowledgement(s?)\b"));

/// Mirrors `structure.py::_struct_002_replacement`: drop the `e`/`E`
/// between `g` (codepoint index 9) and `m` (index 11).
fn struct_002_replacement(matched: &str) -> String {
    let chars: Vec<char> = matched.chars().collect();
    let mut out: String = chars[..10].iter().collect();
    out.extend(&chars[11..]);
    out
}

/// JSS-STRUCT-002 — "Acknowledgments" uses American spelling.
pub fn check_struct_002(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent: &[Slot], idx, node| {
        let Node::Macro(m) = node else { return };
        if !STRUCT_SECTION_MACROS.contains(&m.macroname.as_str()) {
            return;
        }
        let title = first_arg_text(m, parent, idx);
        if !ACKNOWLEDGEMENT_WORD_RE.is_match(&title) {
            return;
        }
        let macro_src: String = parsed.chars[m.span.pos..m.span.end()].iter().collect();
        let (line, col) = lineno_col(&line_index, m.span.pos);
        let fix = ACKNOWLEDGEMENT_WORD_RE.find(&macro_src).map(|found| {
            let matched = found.as_str();
            let replacement = struct_002_replacement(matched);
            let start = m.span.pos + macro_src[..found.start()].chars().count();
            let end = m.span.pos + macro_src[..found.end()].chars().count();
            Fix {
                start,
                end,
                replacement: replacement.clone(),
                description: format!(
                    "Replace {} with American spelling {}.",
                    super::py_repr(matched),
                    super::py_repr(&replacement)
                ),
                confidence: FixConfidence::Safe,
            }
        });
        out.push(make_violation(
            file,
            line,
            Some(col),
            "JSS-STRUCT-002",
            Some("Use 'Acknowledgments' (American spelling) — not 'Acknowledgements'.".to_string()),
            fix,
        ));
    });
    out
}

// --- JSS-STRUCT-003 -------------------------------------------------------

fn walk_envs<'a>(
    nodes: &'a [Node],
    name: &str,
    mut visit: impl FnMut(&'a crate::tex::node::EnvironmentNode),
) {
    walk(nodes, &mut |node, _ancestors| {
        if let Node::Environment(e) = node {
            if e.environmentname == name {
                visit(e);
            }
        }
    });
}

fn is_bare_appendix(title: &str) -> bool {
    matches!(
        title.trim().to_lowercase().as_str(),
        "appendix" | "appendices"
    )
}

/// JSS-STRUCT-003 — appendix sections have descriptive titles.
pub fn check_struct_003(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    walk_envs(&parsed.nodes, "appendix", |env| {
        extract::iter_with_parent_visit(&env.nodelist, &mut |parent: &[Slot], idx, node| {
            let Node::Macro(m) = node else { return };
            if !STRUCT_SECTION_MACROS.contains(&m.macroname.as_str()) {
                return;
            }
            let title = first_arg_text(m, parent, idx);
            if is_bare_appendix(&title) {
                out.push(tex_violation_with_fix(
                    file,
                    &line_index,
                    m.span.pos,
                    "JSS-STRUCT-003",
                    Some(
                        "Give the appendix section a descriptive title (e.g., 'More technical details'), not a bare 'Appendix'."
                            .to_string(),
                    ),
                    None,
                ));
            }
        });
    });
    out
}

/// JSS-STRUCT-004 — no hand-written `thebibliography`.
pub fn check_struct_004(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    walk_envs(&parsed.nodes, "thebibliography", |env| {
        out.push(tex_violation_with_fix(
            file,
            &line_index,
            env.span.pos,
            "JSS-STRUCT-004",
            Some("Replace \\begin{thebibliography}...\\end{thebibliography} with \\bibliography{<bib-file>}.".to_string()),
            None,
        ));
    });
    out
}

// --- JSS-STRUCT-005 -------------------------------------------------------

static TEXT_AND_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\s+and\s+").unwrap());

fn first_group_arg<'a>(
    macro_node: &'a MacroNode,
    parent: &[Slot<'a>],
    idx: usize,
) -> Option<&'a GroupNode> {
    for arg in &macro_node.args {
        if let Some(Node::Group(g)) = arg {
            return Some(g);
        }
    }
    extract::next_group_arg(parent, idx)
}

fn iter_lowercase_and(nodes: &[Node]) -> Vec<&MacroNode> {
    let mut out = Vec::new();
    walk(nodes, &mut |node, _ancestors| {
        if let Node::Macro(m) = node {
            if m.macroname == "and" {
                out.push(m);
            }
        }
    });
    out
}

/// `(chars_node, match_byte_start)` for every whitespace-flanked `and`
/// word at the top level of `group` (not inside nested macros/groups),
/// stopping at the first `\\` row-break macro. Mirrors
/// `structure.py::_iter_text_and_offsets`.
fn iter_text_and_offsets(group: &GroupNode) -> Vec<(&crate::tex::node::CharsNode, usize)> {
    let mut out = Vec::new();
    for child in &group.nodelist {
        match child {
            Node::Macro(m) if m.macroname == "\\" => break,
            Node::Chars(c) => {
                for m in TEXT_AND_RE.find_iter(&c.chars) {
                    out.push((c, m.start()));
                }
            }
            _ => {}
        }
    }
    out
}

/// JSS-STRUCT-005 — `\author{}` separates authors with `\And`/`\AND`.
pub fn check_struct_005(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent: &[Slot], idx, node| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "author" {
            return;
        }
        let Some(group) = first_group_arg(m, parent, idx) else {
            return;
        };

        for and_node in iter_lowercase_and(&group.nodelist) {
            let (line, col) = lineno_col(&line_index, and_node.span.pos);
            let fix = Fix {
                start: and_node.span.pos,
                end: and_node.span.pos + 4, // "\and"
                replacement: "\\And".to_string(),
                description: "Replace lowercase \\and with capitalised \\And — the JSS-canonical author separator."
                    .to_string(),
                confidence: FixConfidence::Safe,
            };
            out.push(make_violation(
                file,
                line,
                Some(col),
                "JSS-STRUCT-005",
                Some("Separate authors with \\And (inline) or \\AND (line break), not lowercase \\and.".to_string()),
                Some(fix),
            ));
        }

        let mut has_macro_separator = false;
        walk(&group.nodelist, &mut |n, _ancestors| {
            if let Node::Macro(mm) = n {
                if matches!(mm.macroname.as_str(), "and" | "And" | "AND") {
                    has_macro_separator = true;
                }
            }
        });
        if has_macro_separator {
            return;
        }
        for (chars_node, offset) in iter_text_and_offsets(group) {
            let Some(m) = TEXT_AND_RE.find_at(&chars_node.chars, offset) else {
                continue;
            };
            let lstripped = m.as_str().trim_start();
            let lead_ws_bytes = m.as_str().len() - lstripped.len();
            let and_start_byte = m.start() + lead_ws_bytes;
            let and_start =
                chars_node.span.pos + chars_node.chars[..and_start_byte].chars().count();
            let and_end = and_start + 3; // "and"
            let (line, col) = lineno_col(&line_index, and_start);
            out.push(make_violation(
                file,
                line,
                Some(col),
                "JSS-STRUCT-005",
                Some("Separate authors with \\And (inline) or \\AND (line break), not the literal word 'and'.".to_string()),
                Some(Fix {
                    start: and_start,
                    end: and_end,
                    replacement: "\\And".to_string(),
                    description: "Replace literal 'and' with \\And — the JSS-canonical author separator.".to_string(),
                    confidence: FixConfidence::Safe,
                }),
            ));
        }
    });
    out
}

// --- JSS-STRUCT-006 -------------------------------------------------------

fn find_bibliography_macro_pos(nodes: &[Node]) -> Option<usize> {
    let mut found = None;
    walk(nodes, &mut |node, _ancestors| {
        if found.is_some() {
            return;
        }
        if let Node::Macro(m) = node {
            if m.macroname == "bibliography" {
                found = Some(m.span.pos);
            }
        }
    });
    found
}

fn find_first_appendix_env(nodes: &[Node]) -> Option<&crate::tex::node::EnvironmentNode> {
    let mut found = None;
    walk_envs(nodes, "appendix", |env| {
        if found.is_none() {
            found = Some(env);
        }
    });
    found
}

fn has_pagebreak_between(nodes: &[Node], start: usize, end: usize) -> bool {
    let mut found = false;
    walk(nodes, &mut |node, _ancestors| {
        if found {
            return;
        }
        if let Node::Macro(m) = node {
            if PAGEBREAK_MACROS.contains(&m.macroname.as_str())
                && start < m.span.pos
                && m.span.pos < end
            {
                found = true;
            }
        }
    });
    found
}

/// JSS-STRUCT-006 — appendix follows the bibliography with a page
/// separator.
pub fn check_struct_006(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    let Some(bib_pos) = find_bibliography_macro_pos(&parsed.nodes) else {
        return out;
    };
    let Some(appendix_env) = find_first_appendix_env(&parsed.nodes) else {
        return out;
    };
    if appendix_env.span.pos <= bib_pos {
        return out;
    }
    if has_pagebreak_between(&parsed.nodes, bib_pos, appendix_env.span.pos) {
        return out;
    }
    out.push(tex_violation_with_fix(
        file,
        &line_index,
        appendix_env.span.pos,
        "JSS-STRUCT-006",
        Some(
            "Insert \\newpage (or \\clearpage) between \\bibliography{} and \\begin{appendix}."
                .to_string(),
        ),
        Some(Fix {
            start: appendix_env.span.pos,
            end: appendix_env.span.pos,
            replacement: "\\newpage\n".to_string(),
            description: "insert \\newpage before \\appendix".to_string(),
            confidence: FixConfidence::Safe,
        }),
    ));
    out
}
