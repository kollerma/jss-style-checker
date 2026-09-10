# Contract: Coloured terminal output

**Plan**: [../plan.md](../plan.md) §8

## C-1 Invariant

The **plain** terminal stream (colour off) is the canonical artifact: it
is byte-identical across engines and is what parity suites, snapshot
tests, and the eval harness compare. Colour never changes layout:
stripping every SGR sequence from coloured output MUST yield the plain
output byte for byte, in each engine.

## C-2 What carries colour (intent)

| Token | Intent | SGR (16-colour set only) |
|---|---|---|
| severity `error`, reviewer `FAIL` | red | `31` |
| severity `warning` | yellow | `33` |
| severity `info` | cyan (blue is unreadable on dark backgrounds) | `36` |
| reviewer `PASS` | green | `32` |
| reviewer `SKIPPED`, confidence suffix `(medium conf.)`, `Overall: n/a` | dim | `2` |
| rule ids, table header cells, banner titles, `Overall:` value | bold | `1` |
| reset | — | `0` |

Nothing is encoded in hue alone: every coloured token remains a word in
the plain text (severity, status, rule id, `(… conf.)`). No 256-colour
or truecolor sequences; light and dark backgrounds both readable.
Footer sentences, the baseline line, and the coverage block body are not
coloured.

## C-3 Decision precedence

One pure function of `(flag, toml_value, env, isatty)`, implemented
identically in `cli.py` and `main.rs` and unit-tested as a matrix:

1. `--color always` → on; `--color never` → off.
2. `NO_COLOR` set and non-empty → off.
3. `CLICOLOR_FORCE` set, non-empty, and not `"0"` → on.
4. TOML `color = "always"|"never"` → that.
5. `auto` (default): on iff stdout is a TTY and `TERM != "dumb"`.

`--output json|sarif|html` and every non-terminal subcommand format are
never coloured. `diff`, `explain`, and `coverage` terminal formats use
the same decision.

## C-4 Escape bytes are per-engine (documented divergence)

The exact SGR byte sequences and their placement are **not** a byte-parity
target and are recorded in `rust/README.md` as a §XIII divergence:

- Python lets rich emit them (`Console(force_terminal=True,
  color_system="standard", width=120)`), using the markup already present
  in `output/terminal.py`.
- Rust wraps cell text in SGR at render time in `terminal.rs`; widths are
  measured on the unstyled text.

Both MUST satisfy C-1 and C-2; they need not agree on, e.g., whether a
reset follows every cell or only every row.

## C-5 Windows

- Python: rich's own console handling (VT where available, legacy win32
  console otherwise). No FFI.
- Rust: `anstream::AutoStream::new(stdout, choice)` in `jsslint-cli` with
  the choice from C-3 (never `AutoStream::auto`); anstream converts SGR
  for legacy consoles and strips it for `Never`. `anstream` is a direct
  dependency of the CLI crate only.
- No Windows CI job exists; the path is verified manually at release.

## C-6 Bindings

WASM, PyO3, and R never colourise; `render()` returns the plain stream.
Documented in `rust/README.md`.

## C-7 Tests

- Unit, both engines: `strip_sgr(render(color=True)) == render(color=False)`
  on author, reviewer, and skipped-rules fixtures; visible width per line
  unchanged; the C-3 matrix.
- `rust/jsslint-core/tests/terminal_parity.rs`: `--color always` cases
  where both sides are SGR-stripped before the byte comparison.
- `rust/jsslint-cli/tests/color_parity.rs`: for `NO_COLOR=1`,
  `CLICOLOR_FORCE=1`, `NO_COLOR=1 --color always`, TOML `color =
  "always"`, `--color never` + `CLICOLOR_FORCE=1`, and `--output json
  --color always`, both CLIs agree on whether `\x1b[` occurs, and the
  stripped bytes are identical.
- Python integration tests run under `CliRunner`, which is never a TTY;
  explicit `--color always` cases are added.

## C-8 Configuration surface

`--color auto|always|never`; TOML `color`; `ToolConfig.color` (Python
`Literal`, Rust `ColorChoice`). The CLI resolves the decision to a bool
and passes it to the renderer; the config object records intent only.
