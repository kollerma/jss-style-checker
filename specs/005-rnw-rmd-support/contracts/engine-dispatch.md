# Contract: engine-level parse dispatch

**Location**: `src/texlint/core/engine.py::parse_document`.

## Signature

```python
def parse_document(
    paths: Sequence[Path],
) -> ParsedDocument: ...
```

Takes a sequence of file paths (from the CLI), dispatches each to the
appropriate parser by extension, and assembles a `ParsedDocument`.

## Dispatch table

```python
_PARSERS: Mapping[str, Callable[[Path], Any]] = {
    ".tex": parse_tex_file,
    ".rnw": parse_rnw_file,
    ".rmd": parse_rmd_file,
    ".bib": parse_bib_file,
}
```

Extension matching is **case-insensitive** (`.Rnw`, `.RMD`, `.BIB`
all accepted).

## Algorithm

```python
def parse_document(paths):
    tex_files, bib_files, rmd_files = [], [], []
    for path in paths:
        suffix = path.suffix.lower()
        parser = _PARSERS.get(suffix)
        if parser is None:
            raise UnsupportedSuffixError(path)  # → CLI exit 2
        result = parser(path)
        if isinstance(result, ParsedTexFile):
            tex_files.append(result)
        elif isinstance(result, ParsedBibFile):
            bib_files.append(result)
        elif isinstance(result, ParsedRmdFile):
            rmd_files.append(result)
    return ParsedDocument(
        tex_files=tuple(tex_files),
        bib_files=tuple(bib_files),
        rmd_files=tuple(rmd_files),
    )
```

## Unknown extensions

- `UnsupportedSuffixError` is caught by `cli.main`; the CLI exits
  with code 2 and a message like:

  ```
  error: unsupported file extension: 'paper.xyz'
    supported: .tex, .bib, .Rnw, .Rmd (case-insensitive)
  ```

- This matches spec 001's existing behaviour for unrecognised files.

## Input-format derivation for `engine.run`

Each parsed-file object carries an internal `_input_format: str`
attribute set by its parser:

| Parser | `_input_format` |
|---|---|
| `parse_tex_file` | `"tex"` |
| `parse_rnw_file` | `"rnw"` (stripped Rnw still returns a `ParsedTexFile` — the format tag is what distinguishes it) |
| `parse_rmd_file` | `"rmd"` |
| `parse_bib_file` | `"bib"` |

`engine.run` unions these into `input_formats` for the rule-dispatch
filter (see `rule-format-filter.md`).

## Invariants

| # | Invariant | Enforcer |
|---|---|---|
| E-1 | `parse_document([])` returns an empty `ParsedDocument`. | `test_empty_paths` |
| E-2 | Mixed input `[paper.tex, paper.Rmd]` returns a `ParsedDocument` with non-empty `tex_files` and non-empty `rmd_files`. | `test_mixed_input` |
| E-3 | Case-insensitive suffix matching: `paper.RNW` dispatches to `parse_rnw_file`. | `test_case_insensitive_suffix` |
| E-4 | Unknown extension → `UnsupportedSuffixError`; CLI exit code 2. | `test_unsupported_suffix_exit_2` |
| E-5 | Parse-time errors inside a parser do NOT propagate; they surface as `JSS-PARSE-000` violations on the returned parsed-file object (Constitution §III). | `test_parse_errors_non_fatal` |
