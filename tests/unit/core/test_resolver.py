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

    def test_bibliography_resolves(self, tmp_path: Path) -> None:
        _write(tmp_path / "refs.bib", "@article{}")
        root = tmp_path / "paper.tex"
        _write(root, r"\bibliography{refs}")
        project = resolve(root)
        assert (tmp_path / "refs.bib").resolve() in project.files

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
