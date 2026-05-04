# Data Model: `jss-lint explain`

**Phase**: 1
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. `Rule` dataclass extension

Three additive fields on the public `texlint.api.Rule`:

| Field           | Type            | Default       | Semantics                                                                  |
| --------------- | --------------- | ------------- | -------------------------------------------------------------------------- |
| `explanation`   | `str`           | (required)    | One-paragraph plain-language explanation (≤120 words).                     |
| `example_bad`   | `str \| None`   | `None`        | Bad-example fragment (literal text). May be `None` for tool-side rules.    |
| `example_good`  | `str \| None`   | `None`        | Good-example fragment.                                                      |

**Validity** (catalogue contract test):
- `explanation` is non-empty for every rule.
- For citable rules (`category in CITABLE_CATEGORIES` from spec
  007), both `example_bad` and `example_good` SHOULD be non-
  `None`; SHOULD here is enforced as a warning, not a hard
  fail, to allow the spec-009 backfill to ship if a few rules
  cannot easily be reduced to a 3–5 line fragment.
- For tool-side rules (`internal`, `parse`), `example_bad` and
  `example_good` MAY be `None`.

## 2. `explain.render` signature

```python
def render(
    rule_id: str | None,
    *,
    fmt: Literal["terminal", "markdown"],
    with_example: bool = False,
    catalogue: tuple[Rule, ...] | None = None,
) -> str: ...
```

| Parameter      | Purpose                                                                                |
| -------------- | -------------------------------------------------------------------------------------- |
| `rule_id`      | Rule id to explain. `None` → listing view.                                             |
| `fmt`          | Output format.                                                                         |
| `with_example` | If True and `rule_id` is set, pull through the `tests/fixtures/violations/<rule>-bad.tex`. |
| `catalogue`    | For testing — defaults to `_catalogue_data.RULES`.                                     |

Return: a single string ending in a newline. The CLI prints it
verbatim to stdout.

## 3. `did_you_mean` signature

```python
def did_you_mean(unknown_id: str, catalogue: tuple[Rule, ...]) -> list[str]:
    ...
```

Returns up to 5 suggestions in deterministic order. Empty list
when nothing close enough; the CLI then falls back to the
category-prefix list (research §4).

## 4. CLI surface

```text
Usage: jss-lint [OPTIONS] [PATHS]...
       jss-lint explain [OPTIONS] [RULE-ID]

Options (root, unchanged from spec 008):
  --journal TEXT
  --mode [author|reviewer]
  --output [terminal|json|html|sarif]
  --ignore-rules TEXT
  --source-root DIR
  --fix / --dry-run / --apply / --fix-rule TEXT
  -v, --verbose

Subcommand `explain`:
  --example                  pull through tests/fixtures/violations/<rule>-bad.tex
  --format [terminal|markdown]   default: terminal
```

The root invocation `jss-lint <PATHS>` continues to work.

## 5. Catalogue contract test extension

Two additions to `tests/unit/test_catalogue.py` (the spec-007
test file):

| Test name                                | Invariant                                                                  |
| ---------------------------------------- | -------------------------------------------------------------------------- |
| `test_every_rule_has_explanation`        | `rule.explanation != ""` for every rule.                                  |
| `test_citable_rules_have_examples` (warn)| `rule.example_bad and rule.example_good` for every rule in `CITABLE_CATEGORIES`. Emitted as a `pytest.warns` (UserWarning) — not a hard fail in spec 009. Becomes a hard fail in a follow-up spec once backfill is complete. |

## 6. Out of scope

| Item                                            | Reason                                                                          |
| ----------------------------------------------- | ------------------------------------------------------------------------------- |
| HTML format                                     | Out per Clarifications.                                                          |
| Paged output                                    | Out per Clarifications.                                                          |
| Per-fragment auto-detect language tag           | Out per research §7.                                                             |
| LLM-generated explanation drafts                | Out — author writes prose by hand.                                                |
| Cross-language fixture autodiscovery            | Out — `.tex` first, then `.Rnw`, then `.Rmd` per research §5.                     |
