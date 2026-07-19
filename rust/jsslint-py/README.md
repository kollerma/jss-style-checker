# jsslint

Native Python binding for the [JSS style checker](https://github.com/kollerma/jss-style-checker)'s Rust core (`jsslint-core`). Lints LaTeX / Sweave / R Markdown manuscripts (`.tex`/`.ltx`/`.Rnw`/`.Rmd` + `.bib`) entirely in memory.

```python
import jsslint

report = jsslint.render(
    [("paper.tex", open("paper.tex").read())],
    output="json",
)
```

See the main project README for the rule catalogue and CLI (`jsslint`/`jss-lint`) documentation.
