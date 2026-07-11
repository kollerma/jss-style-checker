# Build/verification targets for the JSS manuscript.
# `make replicate` is the one-command reproduction entry point.
PY ?= ../.venv-host/bin/python

.PHONY: stats listings pdf lint pages check audit replicate clean

stats:
	cd .. && $(PY) -m tools.generate_paper_stats

listings:
	bash replicate.sh --no-pdf

pdf:
	pdflatex -interaction=nonstopmode -halt-on-error paper.tex
	bibtex paper
	pdflatex -interaction=nonstopmode -halt-on-error paper.tex
	pdflatex -interaction=nonstopmode -halt-on-error paper.tex

lint:
	$(PY) -m texlint.cli paper.tex paper.bib

pages:
	@pdfinfo paper.pdf | awk '/^Pages:/{print "pages:", $$2; exit ($$2 > 34)}'

audit:
	cd .. && $(PY) -m tools.generate_paper_stats --audit

spelling:
	@! grep -nwiE 'capitalis(ation|ed?|ing)|summaris(ed?|ing)|organis(ed?|ation)|normalis(ed?|ation)|minimis(ed?|ing)|analys(ed?|ing)|initialis(ed?|ation)|colour|behaviour|modelling|labelled|licence' paper.tex

check:
	cd .. && $(PY) -m tools.generate_paper_stats --check
	$(MAKE) lint spelling audit

replicate:
	bash replicate.sh

clean:
	rm -f paper.aux paper.bbl paper.blg paper.log paper.out paper.toc paper.pdf
