//! Spec 013 multi-file project resolver — port of
//! `src/texlint/core/resolver.py` plus the `check_project_cycles` /
//! `check_project_missing_refs` violation builders from
//! `journals/jss/rules/project.py`.
//!
//! Filesystem-bound (reads files from disk to walk the reference
//! graph), so — per the design constraint in RESOLVE-PROMPT.md — this
//! lives in the CLI crate, not `jsslint-core`: resolution happens
//! here, then the resolved `(path, contents)` set is handed to the
//! existing fs-agnostic `ParsedDocument::from_sources` / `engine::run`.

use jsslint_core::report::{Severity, Violation};
use regex::Regex;
use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

/// Finds the opening `\macroname{` for each of the four macros; the
/// matching closing brace is then found by manual depth-counting in
/// `find_macro_hits` below (a single-level, non-brace capture can't
/// handle a nested-brace argument like Sweave's
/// `\bibliography{\Sexpr{Rcpp:::bib()}}` — it would stop at the first
/// `}`, landing mid-expression instead of on the real argument).
/// Mirrors `resolver.py::_MACRO_START_RE`.
static MACRO_START_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\\(input|include|subfile|bibliography)\{").unwrap());

/// One `\input{...}`-shaped macro hit, resolved (or not) to a file.
/// Mirrors `resolver.py::ResolvedReference`.
#[derive(Debug, Clone)]
pub struct ResolvedReference {
    pub parent: PathBuf,
    /// Kept for parity with `resolver.py::ResolvedReference.macro` and
    /// exercised by this module's own tests; not read by the
    /// `JSS-PROJECT-002` violation builder (only `.name` is).
    #[allow(dead_code)]
    pub macro_name: &'static str,
    pub name: String,
    pub target: PathBuf,
    pub found: bool,
}

/// Mirrors `resolver.py::ResolvedProject`.
#[derive(Debug, Default)]
pub struct ResolvedProject {
    pub root: PathBuf,
    /// Depth-first visit order (matches `resolver.py::resolve`'s `files`).
    pub files: Vec<PathBuf>,
    pub references: Vec<ResolvedReference>,
    pub missing: Vec<ResolvedReference>,
    /// `(parent, repeated-node)` pairs — the resolver's own simple
    /// cycle bookkeeping (mirrors `resolver.py`'s `cycles` field).
    /// NOT what drives `JSS-PROJECT-001`'s message text — see
    /// `check_project_cycles`, which re-derives cycles from `tree` via
    /// the same dedup-by-node-set DFS as Python's
    /// `journals/jss/rules/project.py::check_project_cycles`.
    pub cycles: Vec<(PathBuf, PathBuf)>,
}

fn texinputs() -> Vec<String> {
    std::env::var("TEXINPUTS")
        .unwrap_or_default()
        .split(':')
        .filter(|p| !p.is_empty())
        .map(str::to_string)
        .collect()
}

fn bibinputs() -> Vec<String> {
    std::env::var("BIBINPUTS")
        .unwrap_or_default()
        .split(':')
        .filter(|p| !p.is_empty())
        .map(str::to_string)
        .collect()
}

const TEX_LIKE_OR_BIB_EXTS: &[&str] = &[".tex", ".ltx", ".Rnw", ".Rmd", ".bib"];

fn has_any_suffix(name: &str, suffixes: &[&str]) -> bool {
    suffixes.iter().any(|s| name.ends_with(s))
}

/// Mirrors `resolver.py::_try_paths`.
fn try_paths(name: &str, search: &[PathBuf]) -> Option<PathBuf> {
    for base in search {
        let candidate = base.join(name);
        if candidate.is_file() {
            return Some(candidate);
        }
        if !has_any_suffix(name, TEX_LIKE_OR_BIB_EXTS) {
            for ext in [".tex", ".ltx"] {
                let with_ext = base.join(format!("{name}{ext}"));
                if with_ext.is_file() {
                    return Some(with_ext);
                }
            }
        }
    }
    None
}

/// Directories to try before TEXINPUTS/BIBINPUTS, in LaTeX's own
/// priority order: the *root* document's directory first, then the
/// *referencing* file's own directory. Mirrors
/// `resolver.py::_local_search_dirs`.
///
/// Real `\input`/`\include` (without the `import`/`subfiles`
/// packages) resolves a relative path against the working directory
/// the TeX engine was invoked in — conventionally the main/root
/// document's directory — for the whole run, not against whichever
/// file issued the nested `\input`. A file two levels deep that does
/// `\input{fig/x}` intending a `fig/` directory that sits beside the
/// *root* (not beside itself) resolves correctly under real LaTeX;
/// resolving only against the immediate parent's directory (this
/// module's original behaviour) reported that as a false-positive
/// missing reference — the observed real-world case (`cran_gems`).
/// Falling back to the parent's own directory second still covers the
/// common single-level case (where they're the same directory anyway)
/// and files that keep siblings together within a subdirectory.
fn local_search_dirs(parent_dir: &Path, root_dir: &Path) -> Vec<PathBuf> {
    if root_dir == parent_dir {
        vec![root_dir.to_path_buf()]
    } else {
        vec![root_dir.to_path_buf(), parent_dir.to_path_buf()]
    }
}

/// Mirrors `resolver.py::_resolve_one`.
fn resolve_one(
    macro_name: &str,
    name: &str,
    parent_dir: &Path,
    root_dir: &Path,
) -> Option<PathBuf> {
    let local_dirs = local_search_dirs(parent_dir, root_dir);
    if macro_name == "bibliography" {
        let bib_name = if name.ends_with(".bib") {
            name.to_string()
        } else {
            format!("{name}.bib")
        };
        for base in &local_dirs {
            let candidate = base.join(&bib_name);
            if candidate.is_file() {
                return Some(candidate);
            }
        }
        for raw in bibinputs().into_iter().chain(texinputs()) {
            let cand = PathBuf::from(&raw).join(&bib_name);
            if cand.is_file() {
                return Some(cand);
            }
        }
        return None;
    }

    if let Some(found) = try_paths(name, &local_dirs) {
        return Some(found);
    }
    let extras: Vec<PathBuf> = texinputs().into_iter().map(PathBuf::from).collect();
    try_paths(name, &extras)
}

const MACRO_NAMES: &[&str] = &["input", "include", "subfile", "bibliography"];

fn macro_static_name(name: &str) -> &'static str {
    MACRO_NAMES
        .iter()
        .find(|m| **m == name)
        .copied()
        .unwrap_or("input")
}

/// Blanks out TeX comments (an unescaped `%` through end of line).
/// Line-based, not verbatim-environment-aware — matches this module's
/// "regex over source text, not a full AST" scope (module doc
/// comment). Sufficient to stop a commented-out
/// `%\bibliography{...}`/`\input{...}` from being treated as a live
/// reference, which is the observed real-world false-positive pattern
/// (recall-corpus papers that comment out an alternate bibliography
/// backend, e.g. `%\bibliography{bibliojss}`). Mirrors
/// `resolver.py::_strip_comments`.
///
/// A backslash always escapes the character after it (so `\%` is a
/// literal percent, not a comment start, and `\\%` — an escaped
/// backslash followed by a real comment — still comments out the rest
/// of the line), matching standard TeX catcode behaviour.
fn strip_comments(text: &str) -> String {
    let mut out_lines: Vec<String> = Vec::new();
    for line in text.split('\n') {
        let chars: Vec<char> = line.chars().collect();
        let mut result = String::with_capacity(line.len());
        let mut i = 0;
        let n = chars.len();
        while i < n {
            let ch = chars[i];
            if ch == '\\' && i + 1 < n {
                result.push(ch);
                result.push(chars[i + 1]);
                i += 2;
                continue;
            }
            if ch == '%' {
                break;
            }
            result.push(ch);
            i += 1;
        }
        out_lines.push(result);
    }
    out_lines.join("\n")
}

/// Finds every `\input{...}` / `\include{...}` / `\subfile{...}` /
/// `\bibliography{...}` hit in `text` (expected to already have TeX
/// comments stripped — see `strip_comments`), in source order,
/// matching balanced braces in the argument. Mirrors
/// `resolver.py::_find_macro_hits`.
///
/// `\bibliography{a,b,c}` is standard BibTeX: a comma-separated list
/// of `.bib` names, each resolved (or missing) independently — not
/// one literal `"a,b,c.bib"` target. Empty entries from a
/// stray/trailing comma are dropped rather than reported as a missing
/// reference.
fn find_macro_hits(text: &str) -> Vec<(&'static str, String)> {
    let bytes = text.as_bytes();
    let mut out = Vec::new();
    for caps in MACRO_START_RE.captures_iter(text) {
        let whole = caps.get(0).unwrap();
        let macro_name = macro_static_name(&caps[1]);
        let start = whole.end();
        let mut depth: i32 = 1;
        let mut i = start;
        while i < bytes.len() && depth > 0 {
            match bytes[i] {
                b'{' => depth += 1,
                b'}' => depth -= 1,
                _ => {}
            }
            i += 1;
        }
        if depth != 0 {
            continue; // unbalanced to EOF — malformed macro, skip it
        }
        let raw_arg = &text[start..i - 1];
        if macro_name == "bibliography" {
            for name in raw_arg.split(',') {
                let trimmed = name.trim();
                if !trimmed.is_empty() {
                    out.push((macro_name, trimmed.to_string()));
                }
            }
        } else {
            out.push((macro_name, raw_arg.trim().to_string()));
        }
    }
    out
}

/// Walks `root`'s `\input`/`\include`/`\subfile`/`\bibliography` graph.
/// Cycle-safe (a file already on the active visit stack is not
/// processed a second time). Mirrors `resolver.py::resolve` exactly.
pub fn resolve(root: &Path) -> ResolvedProject {
    let root = std::fs::canonicalize(root).unwrap_or_else(|_| root.to_path_buf());
    let root_dir = root.parent().unwrap_or(Path::new("")).to_path_buf();
    let mut project = ResolvedProject {
        root: root.clone(),
        ..Default::default()
    };
    let mut visited: HashSet<PathBuf> = HashSet::new();
    let mut stack: Vec<PathBuf> = Vec::new();

    fn visit(
        path: &Path,
        root_dir: &Path,
        visited: &mut HashSet<PathBuf>,
        stack: &mut Vec<PathBuf>,
        project: &mut ResolvedProject,
    ) {
        let path = std::fs::canonicalize(path).unwrap_or_else(|_| path.to_path_buf());
        if stack.contains(&path) {
            let parent = stack.last().cloned().unwrap_or_else(|| path.clone());
            project.cycles.push((parent, path));
            return;
        }
        if visited.contains(&path) {
            return;
        }
        visited.insert(path.clone());
        stack.push(path.clone());
        project.files.push(path.clone());

        // Lenient, violation-free read (mirrors `resolver.py::resolve`'s
        // own `errors="replace"` walk-time read) — a decode wobble
        // never stops the walk; only a genuine I/O failure does
        // (`None`), matching `except OSError: stack.pop(); return`.
        let Some(text) = crate::decode::read_replacing_utf8(&path) else {
            stack.pop();
            return;
        };
        let text = strip_comments(&text);
        let parent_dir = path.parent().unwrap_or(Path::new(""));
        for (macro_name, name) in find_macro_hits(&text) {
            if name.contains('\\') {
                // A computed/dynamic argument (e.g. Sweave's
                // \Sexpr{...}), not a literal filename — nothing to
                // textually resolve, and reporting it as "missing"
                // would be a false positive.
                continue;
            }
            let target = resolve_one(macro_name, &name, parent_dir, root_dir);
            let found = target.is_some();
            let resolved_target = target.unwrap_or_else(|| parent_dir.join(&name));
            project.references.push(ResolvedReference {
                parent: path.clone(),
                macro_name,
                name: name.clone(),
                target: resolved_target.clone(),
                found,
            });
            if !found {
                project.missing.push(ResolvedReference {
                    parent: path.clone(),
                    macro_name,
                    name,
                    target: resolved_target,
                    found: false,
                });
                continue;
            }
            visit(&resolved_target, root_dir, visited, stack, project);
        }
        stack.pop();
    }

    visit(&root, &root_dir, &mut visited, &mut stack, &mut project);
    project
}

/// `JSS-PROJECT-001` — mirrors
/// `journals/jss/rules/project.py::check_project_cycles`: a
/// dedup-by-node-set DFS over the adjacency `tree` (not the
/// resolver's own simplistic `cycles` list), starting from `root`.
/// Each distinct cycle (as a node-set) is reported once, anchored on
/// the node that closes it.
pub fn check_project_cycles(root: &Path, tree: &HashMap<PathBuf, Vec<PathBuf>>) -> Vec<Violation> {
    let mut seen_cycles: HashSet<BTreeSet<PathBuf>> = HashSet::new();
    let mut visited: HashSet<PathBuf> = HashSet::new();
    let mut stack: Vec<PathBuf> = Vec::new();
    let mut violations: Vec<Violation> = Vec::new();

    fn dfs(
        node: &Path,
        tree: &HashMap<PathBuf, Vec<PathBuf>>,
        visited: &mut HashSet<PathBuf>,
        stack: &mut Vec<PathBuf>,
        seen_cycles: &mut HashSet<BTreeSet<PathBuf>>,
        violations: &mut Vec<Violation>,
    ) {
        if let Some(idx) = stack.iter().position(|p| p == node) {
            let mut cycle_nodes: Vec<PathBuf> = stack[idx..].to_vec();
            cycle_nodes.push(node.to_path_buf());
            let cycle_key: BTreeSet<PathBuf> = cycle_nodes.iter().cloned().collect();
            if !seen_cycles.insert(cycle_key) {
                return;
            }
            let chain = cycle_nodes
                .iter()
                .map(|p| p.display().to_string())
                .collect::<Vec<_>>()
                .join(" -> ");
            violations.push(Violation {
                file: node.display().to_string(),
                line: 1,
                column: None,
                rule_id: "JSS-PROJECT-001".to_string(),
                severity: Severity::Error,
                message: format!("cycle detected: {chain}"),
                suggestion: None,
                fix: None,
            });
            return;
        }
        if visited.contains(node) {
            return;
        }
        visited.insert(node.to_path_buf());
        stack.push(node.to_path_buf());
        if let Some(children) = tree.get(node) {
            for child in children {
                dfs(child, tree, visited, stack, seen_cycles, violations);
            }
        }
        stack.pop();
    }

    dfs(
        root,
        tree,
        &mut visited,
        &mut stack,
        &mut seen_cycles,
        &mut violations,
    );
    violations
}

/// `JSS-PROJECT-002` — mirrors
/// `journals/jss/rules/project.py::check_project_missing_refs`: one
/// violation per unresolved reference, anchored on the file that
/// *contained* the reference.
pub fn check_project_missing_refs(missing: &[ResolvedReference]) -> Vec<Violation> {
    missing
        .iter()
        .map(|ref_| Violation {
            file: ref_.parent.display().to_string(),
            line: 1,
            column: None,
            rule_id: "JSS-PROJECT-002".to_string(),
            severity: Severity::Error,
            message: format!("referenced file not found: {}", ref_.name),
            suggestion: None,
            fix: None,
        })
        .collect()
}

/// Builds the adjacency list `check_project_cycles` walks: each
/// resolved (found) reference contributes one edge, deduped, in
/// first-occurrence order. Mirrors `core/engine.py::resolve_project`'s
/// `tree` construction.
pub fn build_tree(project: &ResolvedProject) -> HashMap<PathBuf, Vec<PathBuf>> {
    let mut children: HashMap<PathBuf, Vec<PathBuf>> = HashMap::new();
    for reference in &project.references {
        if !reference.found {
            continue;
        }
        let bucket = children.entry(reference.parent.clone()).or_default();
        if !bucket.contains(&reference.target) {
            bucket.push(reference.target.clone());
        }
    }
    for path in &project.files {
        children.entry(path.clone()).or_default();
    }
    children
}

#[cfg(test)]
mod tests {
    use super::*;

    fn write(path: &Path, text: &str) {
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(path, text).unwrap();
    }

    #[test]
    fn single_file_no_inputs() {
        let dir = tempfile_dir();
        let root = dir.join("paper.tex");
        write(
            &root,
            r"\documentclass{jss} \begin{document} hi \end{document}",
        );
        let project = resolve(&root);
        assert_eq!(project.files.len(), 1);
        assert!(project.references.is_empty());
        assert!(project.missing.is_empty());
        assert!(project.cycles.is_empty());
    }

    #[test]
    fn input_resolves() {
        let dir = tempfile_dir();
        write(&dir.join("intro.tex"), "Intro body.");
        let root = dir.join("paper.tex");
        write(&root, r"\input{intro}");
        let project = resolve(&root);
        assert_eq!(project.files.len(), 2);
        assert!(project.references.iter().all(|r| r.found));
    }

    #[test]
    fn input_with_explicit_extension() {
        let dir = tempfile_dir();
        write(&dir.join("intro.tex"), "Intro.");
        let root = dir.join("paper.tex");
        write(&root, r"\input{intro.tex}");
        let project = resolve(&root);
        assert_eq!(project.files.len(), 2);
    }

    #[test]
    fn missing_input_reported() {
        let dir = tempfile_dir();
        let root = dir.join("paper.tex");
        write(&root, r"\input{ghost}");
        let project = resolve(&root);
        assert_eq!(project.files.len(), 1);
        assert_eq!(project.missing.len(), 1);
        assert_eq!(project.missing[0].macro_name, "input");
        assert_eq!(project.missing[0].name, "ghost");
    }

    #[test]
    fn bibliography_resolves() {
        let dir = tempfile_dir();
        write(&dir.join("refs.bib"), "@article{}");
        let root = dir.join("paper.tex");
        write(&root, r"\bibliography{refs}");
        let project = resolve(&root);
        assert_eq!(project.files.len(), 2);
    }

    #[test]
    fn bibliography_comma_separated_resolves_each_independently() {
        let dir = tempfile_dir();
        write(&dir.join("refs1.bib"), "@article{}");
        write(&dir.join("refs2.bib"), "@article{}");
        let root = dir.join("paper.tex");
        write(&root, r"\bibliography{refs1,refs2}");
        let project = resolve(&root);
        assert_eq!(project.files.len(), 3);
        assert!(project.missing.is_empty());
        assert_eq!(project.references.len(), 2);
        let names: std::collections::HashSet<&str> =
            project.references.iter().map(|r| r.name.as_str()).collect();
        assert_eq!(names, std::collections::HashSet::from(["refs1", "refs2"]));
    }

    #[test]
    fn bibliography_comma_separated_trims_whitespace() {
        let dir = tempfile_dir();
        write(&dir.join("refs1.bib"), "@article{}");
        write(&dir.join("refs2.bib"), "@article{}");
        let root = dir.join("paper.tex");
        write(&root, r"\bibliography{ refs1 , refs2 }");
        let project = resolve(&root);
        assert_eq!(project.files.len(), 3);
        assert!(project.missing.is_empty());
    }

    #[test]
    fn bibliography_comma_separated_reports_only_missing_one() {
        let dir = tempfile_dir();
        write(&dir.join("refs1.bib"), "@article{}");
        let root = dir.join("paper.tex");
        write(&root, r"\bibliography{refs1,ghost}");
        let project = resolve(&root);
        assert_eq!(project.missing.len(), 1);
        assert_eq!(project.missing[0].name, "ghost");
    }

    #[test]
    fn bibliography_trailing_comma_is_ignored() {
        let dir = tempfile_dir();
        write(&dir.join("refs1.bib"), "@article{}");
        let root = dir.join("paper.tex");
        write(&root, r"\bibliography{refs1,}");
        let project = resolve(&root);
        assert!(project.missing.is_empty());
        assert_eq!(project.references.len(), 1);
    }

    #[test]
    fn cycle_detected() {
        let dir = tempfile_dir();
        let a = dir.join("a.tex");
        let b = dir.join("b.tex");
        write(&a, r"\input{b}");
        write(&b, r"\input{a}");
        let project = resolve(&a);
        assert!(!project.cycles.is_empty());
        assert_eq!(project.files.len(), 2);
    }

    #[test]
    fn self_reference_is_cycle() {
        let dir = tempfile_dir();
        let root = dir.join("paper.tex");
        write(&root, r"\input{paper}");
        let project = resolve(&root);
        assert!(!project.cycles.is_empty());
    }

    #[test]
    fn commented_out_input_is_not_a_reference() {
        let dir = tempfile_dir();
        let root = dir.join("paper.tex");
        write(&root, "%\\input{ghost}\n");
        let project = resolve(&root);
        assert!(project.references.is_empty());
        assert!(project.missing.is_empty());
    }

    #[test]
    fn commented_out_bibliography_is_not_a_reference() {
        let dir = tempfile_dir();
        let root = dir.join("paper.tex");
        write(&root, "text before\n%\\bibliography{ghost}\n");
        let project = resolve(&root);
        assert!(project.references.is_empty());
        assert!(project.missing.is_empty());
    }

    #[test]
    fn inline_comment_after_content_still_strips() {
        let dir = tempfile_dir();
        write(&dir.join("intro.tex"), "Intro.");
        let root = dir.join("paper.tex");
        write(
            &root,
            r"\input{intro}  % comment mentioning \bibliography{ghost}",
        );
        let project = resolve(&root);
        assert_eq!(project.references.len(), 1);
        assert_eq!(project.references[0].name, "intro");
    }

    #[test]
    fn escaped_percent_is_not_a_comment() {
        let dir = tempfile_dir();
        write(&dir.join("intro.tex"), "Intro.");
        let root = dir.join("paper.tex");
        write(&root, "100\\% done \\input{intro}\n");
        let project = resolve(&root);
        assert_eq!(project.references.len(), 1);
        assert!(project.references[0].found);
    }

    #[test]
    fn nested_braces_in_argument_are_matched() {
        // Sweave-computed bibliography filename — the argument as a
        // whole isn't a literal filename (it contains a macro
        // invocation), so it must be recognized as unresolvable and
        // silently skipped, not truncated at the first "}" and
        // reported as a spurious missing reference.
        let dir = tempfile_dir();
        let root = dir.join("paper.tex");
        write(&root, r"\bibliography{\Sexpr{Rcpp:::bib()}}");
        let project = resolve(&root);
        assert!(project.references.is_empty());
        assert!(project.missing.is_empty());
    }

    #[test]
    fn dynamic_input_argument_is_skipped_not_missing() {
        let dir = tempfile_dir();
        let root = dir.join("paper.tex");
        write(&root, r"\input{\Sexpr{some_r_call()}}");
        let project = resolve(&root);
        assert!(project.references.is_empty());
        assert!(project.missing.is_empty());
    }

    #[test]
    fn nested_input_resolves_relative_to_root_not_immediate_parent() {
        // root.tex (at the project root) \input's script/technical.tex,
        // which itself \input's fig/figure — a path that only exists
        // relative to the ROOT's directory, not to script/'s own
        // directory. Mirrors real LaTeX \input path semantics (paths
        // resolve against the main document's directory / compile-time
        // CWD, not the file that issued the nested \input) — and the
        // real-world false positive this fixed (cran_gems).
        let dir = tempfile_dir();
        write(&dir.join("fig").join("figure.tex"), "A figure.");
        write(
            &dir.join("script").join("technical.tex"),
            r"\input{fig/figure}",
        );
        let root = dir.join("root.tex");
        write(&root, r"\input{script/technical}");
        let project = resolve(&root);
        assert!(project.missing.is_empty());
        let expected = std::fs::canonicalize(dir.join("fig").join("figure.tex")).unwrap();
        assert!(project.files.contains(&expected));
    }

    #[test]
    fn nested_input_falls_back_to_parent_directory() {
        // sections/a.tex \input's "b", intending sections/b.tex (a
        // sibling within the same subdirectory) — root's own directory
        // doesn't have a matching file, so this must still fall back
        // to a.tex's own directory, not just root's.
        let dir = tempfile_dir();
        write(&dir.join("sections").join("a.tex"), r"\input{b}");
        write(&dir.join("sections").join("b.tex"), "Body.");
        let root = dir.join("root.tex");
        write(&root, r"\input{sections/a}");
        let project = resolve(&root);
        assert!(project.missing.is_empty());
        let expected = std::fs::canonicalize(dir.join("sections").join("b.tex")).unwrap();
        assert!(project.files.contains(&expected));
    }

    #[test]
    fn root_directory_takes_priority_over_parent_directory() {
        // Both root_dir/b.tex and sections/b.tex exist; real LaTeX
        // (CWD == root's directory for the whole compile) would pick
        // the root-relative one, not the parent-relative one.
        let dir = tempfile_dir();
        write(&dir.join("b.tex"), "Root-level b.");
        write(&dir.join("sections").join("a.tex"), r"\input{b}");
        write(&dir.join("sections").join("b.tex"), "Sibling b.");
        let root = dir.join("root.tex");
        write(&root, r"\input{sections/a}");
        let project = resolve(&root);
        let reference = project
            .references
            .iter()
            .find(|r| r.name == "b")
            .expect("reference to b");
        let expected = std::fs::canonicalize(dir.join("b.tex")).unwrap();
        assert_eq!(reference.target, expected);
    }

    #[test]
    fn check_project_cycles_two_node_emits_single_violation() {
        let dir = tempfile_dir();
        let a = dir.join("a.tex");
        let b = dir.join("b.tex");
        write(&a, r"\input{b}");
        write(&b, r"\input{a}");
        let project = resolve(&a);
        let tree = build_tree(&project);
        let violations = check_project_cycles(&project.root, &tree);
        assert_eq!(violations.len(), 1);
        assert_eq!(violations[0].rule_id, "JSS-PROJECT-001");
        assert!(violations[0].message.contains("cycle detected"));
    }

    #[test]
    fn check_project_missing_refs_one_per_entry() {
        let dir = tempfile_dir();
        let root = dir.join("paper.tex");
        write(&root, r"\input{ghost}");
        let project = resolve(&root);
        let violations = check_project_missing_refs(&project.missing);
        assert_eq!(violations.len(), 1);
        assert_eq!(violations[0].rule_id, "JSS-PROJECT-002");
        assert_eq!(violations[0].message, "referenced file not found: ghost");
    }

    fn tempfile_dir() -> PathBuf {
        let dir = std::env::temp_dir().join(format!(
            "jsslint-resolver-test-{}-{}",
            std::process::id(),
            COUNTER.fetch_add(1, std::sync::atomic::Ordering::SeqCst)
        ));
        std::fs::create_dir_all(&dir).unwrap();
        dir
    }

    static COUNTER: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
}
