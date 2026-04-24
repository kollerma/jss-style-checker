# Contract: `.Rmd` tokenizer

**Location**: `src/texlint/core/rmd_parser.py`.
**Entry point**: `parse_rmd_source(path: Path, src: str) -> ParsedRmdFile`.

## Signature

```python
def parse_rmd_source(path: Path, src: str) -> ParsedRmdFile: ...
def parse_rmd_file(path: Path) -> ParsedRmdFile: ...  # reads path, delegates
```

Pure function. No imports of `markdown-it-py` / `mistune` / similar.
`yaml.safe_load` is the only external parser call.

## Tokenizer state machine

```text
state = START
buffer = []
for 1-based line_no, line in enumerate(src.splitlines(), start=1):

  START:
    if line.strip() == "---":
        state = FRONTMATTER
        buffer = []
        frontmatter_start = line_no
    else:
        state = BODY  (reprocess line via BODY handler)

  FRONTMATTER:
    if line.strip() == "---":
        frontmatter = yaml.safe_load("\n".join(buffer)) or {}
        state = BODY
    else:
        buffer.append(line)

  BODY:
    if re.match(r"^```(\{.*\})?\s*$", line):
        open_fence_line = line_no
        fence_info = _extract_fence_lang(line)  # may be '' for plain ```
        state = FENCE
        fence_body = []
    elif re.match(r"^(#+)\s+(.+)$", line):
        headings.append(RmdHeading(level=len(g1), text=g2, line=line_no))
    else:
        prose_buffer.append((line_no, line))
        # Flush prose_buffer to RmdProse on blank line or end-of-body.

  FENCE:
    if re.match(r"^```\s*$", line):
        code_blocks.append(RmdCode(
            lang=fence_info, body="\n".join(fence_body),
            open_line=open_fence_line, close_line=line_no,
        ))
        state = BODY
    else:
        fence_body.append(line)
```

## Post-tokenization pass: inline R code stripping in prose

For each `RmdProse` block:

```python
_INLINE_R = re.compile(r"`r\s[^`]*`")
prose.text = _INLINE_R.sub(lambda m: " " * len(m.group(0)), prose.text)
```

Equivalent-width whitespace so column offsets stay meaningful.

## Raw-LaTeX island extraction

After prose blocks are populated:

```python
for prose in prose_blocks:
    fragment = parse_tex_source(prose.text, path=f"{rmd.path}:block@{prose.line}")
    latex_fragments.append(fragment)
```

All pylatexenc line numbers inside a fragment are local (1-based within
the prose block). The engine offsets them to source-space at violation
time: `source_line = prose.line + fragment_line - 1`.

## Invariants

| # | Invariant | Enforcer |
|---|---|---|
| M-1 | Token start lines are strictly increasing within each token tuple. | `test_rmd_token_ordering` |
| M-2 | Every line in `src` is attributable to exactly one token region (frontmatter, heading, prose, code). Boundary lines (fences, `---`) belong to the fence / frontmatter token. | `test_line_coverage_complete` |
| M-3 | Malformed YAML → `yaml_frontmatter = {}` + one `JSS-PARSE-000` violation with `line = frontmatter_start`. No crash. | `test_malformed_yaml_graceful` |
| M-4 | Unterminated fence (open `` ``` `` with no close before EOF) → one `JSS-PARSE-000` violation with `line = open_fence_line`. Remaining lines are NOT treated as prose. | `test_unterminated_fence_graceful` |
| M-5 | Unterminated frontmatter (leading `---` with no close) → one `JSS-PARSE-000` violation with `line = frontmatter_start`; body parsing continues from the line after the leading `---` (treat as if frontmatter were empty). | `test_unterminated_frontmatter_graceful` |
| M-6 | Inline `` `r expr` `` is stripped to spaces of equal byte length; other backtick spans (`` `code` `` without leading `r `) are left untouched. | `test_inline_r_only` |
| M-7 | A fence whose opening line uses `{r, ...}` info is a code block (R code). The language-tag heuristic: anything matching `\{r(,.*)?\}` → `lang="r"`. | `test_fence_r_tag` |

## Test matrix

| Case | Expectation |
|---|---|
| Empty `.Rmd` | `frontmatter={}`, all token tuples empty, no violations. |
| Frontmatter only | `frontmatter` populated; no headings / prose / code. |
| Frontmatter + body | Both populated; line numbers contiguous. |
| Body only (no leading `---`) | `frontmatter={}`, body parsed from line 1. |
| Multiple headings | All captured with correct levels and line numbers. |
| Fenced code with `{r}` tag | `lang="r"`; body content captured verbatim. |
| Fenced code with `{python}` tag | `lang="python"`; still a `RmdCode` (rules skip it). |
| Plain `` ``` `` fence (no info string) | `lang=""`. |
| Prose with inline `` `r runif(1)` `` | Prose text has equal-width whitespace at the inline-code position. |
| Prose with inline `` `code` `` (no `r ` prefix) | Left unchanged. |
| Malformed YAML (tab indent, etc.) | Single `JSS-PARSE-000` on frontmatter-start line. |
| Unterminated fence | `JSS-PARSE-000` on fence-open line. |
| Unterminated frontmatter | `JSS-PARSE-000` on frontmatter-start; body continues. |
| Prose with raw `$x^2$` inline math | `RmdProse` captures text; `latex_fragments` has a `ParsedTexFile` with a `LatexMathNode`. |
| Prose with `\begin{equation}…\end{equation}` | Same; pylatexenc parses the environment inside the fragment. |
