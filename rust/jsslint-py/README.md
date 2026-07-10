# jsslint

Native Python binding for the [JSS style checker](https://github.com/kollerma/jss-style-checker-dev)'s Rust core (`jsslint-core`).

```python
import jsslint

report = jsslint.render(
    [("paper.tex", open("paper.tex").read())],
    output="json",
)
```

See the main project README for the rule catalogue and CLI (`jsslint`/`jss-lint`) documentation.
