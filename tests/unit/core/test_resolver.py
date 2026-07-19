"""Spec 013 — multi-file resolver tests."""

from __future__ import annotations

from pathlib import Path

from texlint.core.resolver import resolve


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class TestResolve:
    def test_single_file_no_inputs(self, tmp_path: Path) -> None:
        root = tmp_path / "paper.tex"
        _write(root, r"\documentclass{jss} \begin{document} hi \end{document}")
        project = resolve(root)
        assert len(project.files) == 1
        assert project.references == ()
        assert project.missing == ()
        assert project.cycles == ()

    def test_input_resolves(self, tmp_path: Path) -> None:
        _write(tmp_path / "intro.tex", "Intro body.")
        root = tmp_path / "paper.tex"
        _write(root, r"\input{intro}")
        project = resolve(root)
        assert len(project.files) == 2
        assert (tmp_path / "intro.tex").resolve() in project.files
        assert all(r.found for r in project.references)

    def test_input_with_explicit_extension(self, tmp_path: Path) -> None:
        _write(tmp_path / "intro.tex", "Intro.")
        root = tmp_path / "paper.tex"
        _write(root, r"\input{intro.tex}")
        project = resolve(root)
        assert len(project.files) == 2

    def test_missing_input_reported(self, tmp_path: Path) -> None:
        root = tmp_path / "paper.tex"
        _write(root, r"\input{ghost}")
        project = resolve(root)
        assert len(project.files) == 1
        assert len(project.missing) == 1
        assert project.missing[0].macro == "input"
        assert project.missing[0].name == "ghost"
        assert project.missing[0].parent == root.resolve()

    def test_bibliography_resolves(self, tmp_path: Path) -> None:
        _write(tmp_path / "refs.bib", "@article{}")
        root = tmp_path / "paper.tex"
        _write(root, r"\bibliography{refs}")
        project = resolve(root)
        assert (tmp_path / "refs.bib").resolve() in project.files

    def test_bibliography_comma_separated_resolves_each_independently(
        self, tmp_path: Path
    ) -> None:
        _write(tmp_path / "refs1.bib", "@article{}")
        _write(tmp_path / "refs2.bib", "@article{}")
        root = tmp_path / "paper.tex"
        _write(root, r"\bibliography{refs1,refs2}")
        project = resolve(root)
        assert (tmp_path / "refs1.bib").resolve() in project.files
        assert (tmp_path / "refs2.bib").resolve() in project.files
        assert project.missing == ()
        assert len(project.references) == 2
        assert {r.name for r in project.references} == {"refs1", "refs2"}

    def test_bibliography_comma_separated_trims_whitespace(
        self, tmp_path: Path
    ) -> None:
        _write(tmp_path / "refs1.bib", "@article{}")
        _write(tmp_path / "refs2.bib", "@article{}")
        root = tmp_path / "paper.tex"
        _write(root, r"\bibliography{ refs1 , refs2 }")
        project = resolve(root)
        assert (tmp_path / "refs1.bib").resolve() in project.files
        assert (tmp_path / "refs2.bib").resolve() in project.files
        assert project.missing == ()

    def test_bibliography_comma_separated_reports_only_missing_one(
        self, tmp_path: Path
    ) -> None:
        _write(tmp_path / "refs1.bib", "@article{}")
        root = tmp_path / "paper.tex"
        _write(root, r"\bibliography{refs1,ghost}")
        project = resolve(root)
        assert (tmp_path / "refs1.bib").resolve() in project.files
        assert len(project.missing) == 1
        assert project.missing[0].name == "ghost"

    def test_bibliography_trailing_comma_is_ignored(self, tmp_path: Path) -> None:
        _write(tmp_path / "refs1.bib", "@article{}")
        root = tmp_path / "paper.tex"
        _write(root, r"\bibliography{refs1,}")
        project = resolve(root)
        assert (tmp_path / "refs1.bib").resolve() in project.files
        assert project.missing == ()
        assert len(project.references) == 1

    def test_cycle_detected(self, tmp_path: Path) -> None:
        a = tmp_path / "a.tex"
        b = tmp_path / "b.tex"
        _write(a, r"\input{b}")
        _write(b, r"\input{a}")
        project = resolve(a)
        assert len(project.cycles) >= 1
        # Both files visited exactly once.
        assert len(project.files) == 2

    def test_self_reference_is_cycle(self, tmp_path: Path) -> None:
        root = tmp_path / "paper.tex"
        _write(root, r"\input{paper}")
        project = resolve(root)
        assert project.cycles

    def test_commented_out_input_is_not_a_reference(self, tmp_path: Path) -> None:
        root = tmp_path / "paper.tex"
        _write(root, "%\\input{ghost}\n")
        project = resolve(root)
        assert project.references == ()
        assert project.missing == ()

    def test_commented_out_bibliography_is_not_a_reference(
        self, tmp_path: Path
    ) -> None:
        root = tmp_path / "paper.tex"
        _write(root, "text before\n%\\bibliography{ghost}\n")
        project = resolve(root)
        assert project.references == ()
        assert project.missing == ()

    def test_inline_comment_after_content_still_strips(self, tmp_path: Path) -> None:
        _write(tmp_path / "intro.tex", "Intro.")
        root = tmp_path / "paper.tex"
        _write(root, r"\input{intro}  % comment mentioning \bibliography{ghost}")
        project = resolve(root)
        assert len(project.references) == 1
        assert project.references[0].name == "intro"

    def test_escaped_percent_is_not_a_comment(self, tmp_path: Path) -> None:
        _write(tmp_path / "intro.tex", "Intro.")
        root = tmp_path / "paper.tex"
        _write(root, "100\\% done \\input{intro}\n")
        project = resolve(root)
        assert len(project.references) == 1
        assert project.references[0].found

    def test_nested_braces_in_argument_are_matched(self, tmp_path: Path) -> None:
        # Sweave-computed bibliography filename — the argument as a
        # whole isn't a literal filename (it contains a macro
        # invocation), so it must be recognized as unresolvable and
        # silently skipped, not truncated at the first "}" and
        # reported as a spurious missing reference.
        root = tmp_path / "paper.tex"
        _write(root, r"\bibliography{\Sexpr{Rcpp:::bib()}}")
        project = resolve(root)
        assert project.references == ()
        assert project.missing == ()

    def test_dynamic_input_argument_is_skipped_not_missing(
        self, tmp_path: Path
    ) -> None:
        root = tmp_path / "paper.tex"
        _write(root, r"\input{\Sexpr{some_r_call()}}")
        project = resolve(root)
        assert project.references == ()
        assert project.missing == ()

    def test_nested_input_resolves_relative_to_root_not_immediate_parent(
        self, tmp_path: Path
    ) -> None:
        # root.tex (at the project root) \input's script/technical.tex,
        # which itself \input's fig/figure — a path that only exists
        # relative to the ROOT's directory, not to script/'s own
        # directory. Mirrors real LaTeX \input path semantics (paths
        # resolve against the main document's directory / compile-time
        # CWD, not the file that issued the nested \input) — and the
        # real-world false positive this fixed (cran_gems).
        _write(tmp_path / "fig" / "figure.tex", "A figure.")
        _write(tmp_path / "script" / "technical.tex", r"\input{fig/figure}")
        root = tmp_path / "root.tex"
        _write(root, r"\input{script/technical}")
        project = resolve(root)
        assert project.missing == ()
        assert (tmp_path / "fig" / "figure.tex").resolve() in project.files

    def test_nested_input_falls_back_to_parent_directory(
        self, tmp_path: Path
    ) -> None:
        # sections/a.tex \input's "b", intending sections/b.tex (a
        # sibling within the same subdirectory) — root's own directory
        # doesn't have a matching file, so this must still fall back
        # to a.tex's own directory, not just root's.
        _write(tmp_path / "sections" / "a.tex", r"\input{b}")
        _write(tmp_path / "sections" / "b.tex", "Body.")
        root = tmp_path / "root.tex"
        _write(root, r"\input{sections/a}")
        project = resolve(root)
        assert project.missing == ()
        assert (tmp_path / "sections" / "b.tex").resolve() in project.files

    def test_root_directory_takes_priority_over_parent_directory(
        self, tmp_path: Path
    ) -> None:
        # Both root_dir/b.tex and sections/b.tex exist; real LaTeX
        # (CWD == root's directory for the whole compile) would pick
        # the root-relative one, not the parent-relative one.
        _write(tmp_path / "b.tex", "Root-level b.")
        _write(tmp_path / "sections" / "a.tex", r"\input{b}")
        _write(tmp_path / "sections" / "b.tex", "Sibling b.")
        root = tmp_path / "root.tex"
        _write(root, r"\input{sections/a}")
        project = resolve(root)
        ref = next(r for r in project.references if r.name == "b")
        assert ref.target == (tmp_path / "b.tex").resolve()
