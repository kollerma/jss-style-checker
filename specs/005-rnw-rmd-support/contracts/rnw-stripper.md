# Contract: `.Rnw` chunk stripper

**Location**: `src/texlint/core/parser.py::strip_rnw_chunks`.
**Invocation path**: `parse_rnw_file` → `strip_rnw_chunks` → `parse_tex_file`.

## Signature

```python
def strip_rnw_chunks(src: str) -> str: ...
```

Pure function. No I/O, no state, no randomness. Same `src` → same
result byte-for-byte.

## Behaviour

Given source text containing Sweave / knitr chunk blocks of the form

```
<<[label][, opt=val]*>>=
... R code ...
@
```

replaces each matched chunk with a whitespace string of **equal
newline count and equal byte length** (where possible), then returns
the result.

Also strips inline `\Sexpr{...}` calls to equivalent-length spaces
(single-line, no newline preservation needed).

## Invariants

| # | Invariant | Enforcer |
|---|---|---|
| S-1 | `strip_rnw_chunks(src).count("\n") == src.count("\n")` for any `src`. | `test_line_count_invariant` |
| S-2 | Substrings outside chunks are byte-identical in input and output. | `test_outside_chunks_preserved` |
| S-3 | Chunk body lines (between `<<...>>=` and `@`) are replaced with newlines only (no spaces, tabs, or `%` comments) so they parse to empty chars nodes in pylatexenc. | `test_chunk_body_is_blank` |
| S-4 | `\Sexpr{…}` is replaced by spaces of the same byte length (no newlines to preserve — inline only). | `test_sexpr_inline_stripped` |
| S-5 | Unclosed chunk (an `<<...>>=` with no following `^@\s*$`) is left unchanged; the caller surfaces it as `JSS-PARSE-000` via pylatexenc's normal parse path. | `test_unclosed_chunk_passthrough` |
| S-6 | A literal `@` on its own line that is NOT a chunk close (e.g., commented-out, or inside a non-chunk context) is left unchanged. | `test_bare_at_sign_not_closed` |

## Regex (pinned)

```python
_RNW_CHUNK = re.compile(
    r"<<[^>]*>>=\n.*?^@\s*$",
    re.DOTALL | re.MULTILINE,
)

_RNW_SEXPR = re.compile(r"\\Sexpr\{[^{}]*\}")
```

## Test matrix

| Case | Expectation |
|---|---|
| Empty string | Returns `""`. |
| No chunks | Returns `src` unchanged byte-for-byte. |
| Single chunk | Chunk body → newlines; surrounding text preserved. |
| Multiple non-overlapping chunks | All stripped; newline count preserved. |
| Chunk with options `<<fig.width=5, cache=TRUE>>=` | Stripped. |
| Chunk with no label `<<>>=` | Stripped. |
| Unclosed chunk (EOF before `@`) | Left unchanged (passes to pylatexenc which emits a parse error). |
| Bare `@` on its own line outside any chunk | Left unchanged. |
| Nested `<<...>>=` inside a chunk body | Outer chunk matches lazily to the first `^@\s*$`; inner delimiter is swallowed as body. |
| Inline `\Sexpr{round(pi, 3)}` outside any chunk | Stripped to spaces of equal length. |
| Inline `\Sexpr{}` with braces containing braces (`{foo{bar}}`) | Rejected by `[^{}]*` regex; NOT stripped. Documented limitation. |
