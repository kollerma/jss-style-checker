# Contract: Annotation File Schema

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

This contract documents the byte-level invariants of an
`annotations.toml` file. Every file in
`eval/recall-corpus/<paper-id>/annotations.toml` MUST
conform.

## C-1 Top-level structure

```toml
[meta]
paper_id = "<id>"
annotator = "<name>"
date = "<ISO-8601>"
notes = "<optional>"

[[violations]]
rule_id = "..."
file = "..."
line = 42
comment = "<optional>"
```

Two top-level tables: `meta` and the array-of-tables
`violations`. No other top-level keys are permitted.

## C-2 `meta` fields

| Field      | Type    | Required | Notes                                              |
| ---------- | ------- | -------- | -------------------------------------------------- |
| `paper_id` | string  | yes      | Equals the directory name.                          |
| `annotator`| string  | yes      | Free text; convention: `"Manuel Koller"` for v1.    |
| `date`     | string  | yes      | ISO-8601 calendar (`YYYY-MM-DD`).                   |
| `notes`    | string  | no       | Free text; one paragraph max.                       |

## C-3 `violations` entries

Each entry is a TOML table with these fields:

| Field      | Type    | Required | Notes                                              |
| ---------- | ------- | -------- | -------------------------------------------------- |
| `rule_id`  | string  | yes      | Must exist in the catalogue (warning on retired ids).|
| `file`     | string  | yes      | Relative path under the paper's directory.          |
| `line`     | int ≥1  | yes      | 1-based line number; ≤ file's line count.            |
| `comment`  | string  | no       | One-line free text.                                 |

`column` does NOT participate (matches the spec-016
identity tuple convention; column drift in source edits
shouldn't invalidate annotations).

## C-4 Empty corpus

A paper with zero violations is legal. Its `annotations.toml`:

```toml
[meta]
paper_id = "..."
annotator = "..."
date = "..."

# (no [[violations]] entries)
```

## C-5 Validation behaviour

`eval-jss recall --validate`:
- Parses every annotation file.
- For each, asserts C-1 to C-4.
- For each `rule_id`: checks catalogue membership
  (warning if retired; error if never existed).
- For each `(file, line)`: checks the line exists in the
  named source file.
- Exits 0 on full-corpus pass; 2 with a per-file error
  list on any failure.

## C-6 Hashing

`eval/recall-corpus/corpus-manifest.csv` lists each
paper's source SHA256. The recall harness verifies the
hash on every run; a mismatch fails the run with a
"corpus drift" error.

## C-7 No external references

Annotation files MUST NOT reference rules from external
journals or rules not present in `_catalogue_data.RULES`.
If a future spec adds a journal or rule, the recall
corpus's annotations may be extended; until then, only
JSS rules are valid.

## C-8 Backwards compatibility

The schema is additive. Future fields (e.g.,
`severity_override`, `annotator_confidence`) MAY be added
as optional fields without invalidating prior
annotation files. Removed fields require a migration
and a corpus-wide replay.
