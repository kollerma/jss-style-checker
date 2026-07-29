# Build/verification targets for the JSS manuscript.
# `make regenerate` is the one-command manuscript-regeneration gate
# (internal, needs the repo); `make replicate` runs the reviewer-facing
# replication script against the released tool; `make bundle` assembles
# the submission upload set into <repo>/submission/.
PY ?= ../.venv-host/bin/python

.PHONY: stats listings pdf lint pages check audit regenerate replicate \
        bundle clean

stats:
	cd .. && $(PY) -m tools.generate_paper_stats

listings:
	bash regenerate.sh --no-pdf

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
	@! grep -nwiE 'capitalis(ation|ed?|ing)|summaris(ed?|ing)|organis(ed?|ation)|normalis(ed?|ation)|minimis(ed?|ing)|analys(ed?|ing)|initialis(ed?|ation)|colour|behaviour|modelling|labelled|licence' paper.tex generated/*.tex

check:
	cd .. && $(PY) -m tools.generate_paper_stats --check
	$(MAKE) lint spelling audit

regenerate:
	bash regenerate.sh

replicate:
	bash replicate.sh

bundle:
	bash bundle.sh

clean:
	rm -f paper.aux paper.bbl paper.blg paper.log paper.out paper.toc paper.pdf
