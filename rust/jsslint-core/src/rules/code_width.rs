//! Code-width rule — mirrors `journals/jss/rules/code_width.py`
//! (JSS-WIDTH-001).

use super::tex_common::{lineno_col, make_violation};
use crate::report::Violation;
use crate::tex::node::Node;
use crate::tex::prose::{walk, CODE_DISPLAY_ENVS};
use crate::tex::{position::LineIndex, ParsedTex};

/// JSS-WIDTH-001 — code lines inside code-display environments
/// (Sinput/Soutput/CodeInput/CodeOutput/verbatim/Verbatim/Code/Scode)
/// must fit within `code_width` columns. `column` on the returned
/// violation is deliberately the offending *length*, not a real
/// column — matches `code_width.py::_violation`'s documented quirk
/// (width violations are line-anchored, not position-anchored).
pub fn check_width_001(file: &str, parsed: &ParsedTex, code_width: u32) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    walk(&parsed.nodes, &mut |node, _ancestors| {
        let Node::Environment(env) = node else { return };
        if !CODE_DISPLAY_ENVS.contains(&env.environmentname.as_str()) {
            return;
        }
        let (Some(start_pos), Some(end_pos)) = content_span(&env.nodelist) else {
            return;
        };
        let content: String = parsed.chars[start_pos..end_pos].iter().collect();
        let (start_line, _) = lineno_col(&line_index, start_pos);
        for (offset, raw_line) in content.split('\n').enumerate() {
            let line_text = raw_line.strip_suffix('\r').unwrap_or(raw_line);
            let width = line_text.trim_end().chars().count() as u32;
            if width <= code_width {
                continue;
            }
            out.push(make_violation(
                file,
                start_line + offset as u32,
                Some(width),
                "JSS-WIDTH-001",
                Some(format!(
                    "Wrap or reflow the code line to fit in {code_width} columns."
                )),
                None,
            ));
        }
    });
    out
}

/// `[start, end)` codepoint span between the environment's first and
/// last child. Mirrors `code_width.py::_env_content_span`.
fn content_span(nodelist: &[Node]) -> (Option<usize>, Option<usize>) {
    let (Some(first), Some(last)) = (nodelist.first(), nodelist.last()) else {
        return (None, None);
    };
    (Some(first.span().pos), Some(last.span().end()))
}
