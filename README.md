# jss-style-checker

Style checker for manuscripts submitted to the
[Journal of Statistical Software](https://www.jstatsoft.org/) (JSS).

The package ships:

- `jss-lint`, a command-line entry point.
- `texlint`, an importable Python library.

## Install (development)

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

## Usage

```sh
jss-lint --help
```

## Development

Helper scripts activate the project `.venv` and forward their arguments:

- `scripts/vpy.sh`  — run Python.
- `scripts/vlint.sh` — run `ruff` (default: `ruff check .`).
- `scripts/vtest.sh` — run `pytest`. Supports `--tail=N` and `--grep=PATTERN`
  to replace `| tail` / `| grep` idioms.

## License

MIT — see [LICENSE](LICENSE).
