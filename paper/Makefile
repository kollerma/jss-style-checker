# Build/verification targets for the JSS manuscript.
# `make regenerate` is the one-command manuscript-regeneration gate
# (internal, needs the repo); `make replicate` runs the reviewer-facing
# replication script against the released tool; `make bundle` assembles
# the submission upload set and `make arxiv` the arXiv source tarball,
# both into <repo>/submission/.
# .venv-host is the macOS host's venv, .venv the one a Linux container or
# CI creates; the host venv's interpreter is a dangling symlink anywhere
# else, so prefer it only when it actually executes.
PY ?= $(shell [ -x ../.venv-host/bin/python ] && echo ../.venv-host/bin/python || echo ../.venv/bin/python)

.PHONY: stats listings pdf lint pages check audit regenerate replicate \
        bundle arxiv joss joss-pdf clean

stats:
	cd .. && $(PY) -m tools.generate_paper_stats

# Regenerate the JOSS paper (joss/paper.md from joss/paper.md.in); the
# word-count bound (750-1750) and placeholder substitution are enforced
# inside the generator, and drift is covered by `make check`.
joss: stats

# Render joss/paper.md with JOSS's own toolchain (needs docker).
joss-pdf:
	docker run --rm -v $(CURDIR)/joss:/data -u $$(id -u):$$(id -g) \
	  openjournals/inara -o pdf paper.md

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
	@! grep -nwiE 'capitalis(ation|ed?|ing)|summaris(ed?|ing)|organis(ed?|ation)|normalis(ed?|ation)|minimis(ed?|ing)|analys(ed?|ing)|initialis(ed?|ation)|colour|behaviour|modelling|labelled|licence' paper.tex generated/*.tex joss/paper.md.in

check:
	cd .. && $(PY) -m tools.generate_paper_stats --check
	$(MAKE) lint spelling audit

regenerate:
	bash regenerate.sh

replicate:
	bash replicate.sh

bundle:
	bash bundle.sh

arxiv:
	bash arxiv.sh

clean:
	rm -f paper.aux paper.bbl paper.blg paper.log paper.out paper.toc paper.pdf
