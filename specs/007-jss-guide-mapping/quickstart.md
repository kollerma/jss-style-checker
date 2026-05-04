# Quickstart: Adding or Updating a Rule's JSS-guide Citation

**Audience**: contributors adding a new rule to the catalogue, or
updating a rule's `guide_section` / `guide_url` after a JSS guide
re-publication.

## Prerequisites

- Python ≥3.10, dev extras installed.
- Repo at HEAD on the spec-007 branch (or post-merge `main`).

## Where things live

```text
src/texlint/api.py                                  # Rule dataclass
src/texlint/journals/_catalogue_data.py             # 58-rule catalogue
src/texlint/journals/jss/_guide_index.py            # tiny loader
docs/jss-guide/index.json                           # central URL map
tests/unit/test_catalogue.py                        # contract tests
```

## Adding a new citable rule

1. Pick the JSS-guide section that defines the rule, in the form
   `§<n>[.<m>] <Title>`. Look at the existing catalogue entries
   for the canonical phrasing (e.g., `"§3.2 Citations"`).
2. Open `docs/jss-guide/index.json`. If your section already
   appears, note the URL. Otherwise, add a new entry mapping
   the section label to the public JSS author-guide URL
   (anchor-deep-link if available; page-level otherwise).
3. Add the new rule to `_catalogue_data.RULES` with `guide_section`
   set to the section label and `guide_url` set to the matching
   URL from `index.json`.
4. Run the catalogue contract tests:
   ```sh
   pytest tests/unit/test_catalogue.py -v
   ```
   Both tests must pass. If either fails, the message names the
   rule id and the violated invariant; fix per the message.
5. Run the renderer tests; goldens may need a pass:
   ```sh
   pytest tests/unit/output/ -v
   ```

## Adding a new tool-side rule

1. Add the rule with `category` in `{"internal", "parse"}`.
2. Set `guide_section = "internal"` and `guide_url = None`.
3. Run `pytest tests/unit/test_catalogue.py`. The sentinel
   path is the only valid way to opt out of a real citation.

## Updating URLs after a JSS guide republication

1. Edit `docs/jss-guide/index.json`, changing the URL value for
   each affected section. Keep the keys (section labels) the
   same — they are also the values of `Rule.guide_section`.
2. Run `pytest tests/unit/test_catalogue.py`. The
   `test_guide_urls_resolve_through_index` test will fail if
   any rule's `guide_url` now disagrees with the index.
3. To fix, run a single mechanical pass through
   `_catalogue_data.RULES`:
   - For every citable rule, set `guide_url =
     load_guide_index()[rule.guide_section]`.
   - You can do this with a one-shot script; it is a pure
     mechanical transform.
4. Re-run the contract tests; they should now pass.

## Updating section labels (rare)

Section labels change rarely. When they do (e.g., the JSS guide
renames `§3.2 Citations` to `§3.2 References`):

1. Edit `index.json`: rename the key.
2. Update every `_catalogue_data.RULES` entry whose
   `guide_section` matches the old label.
3. Re-run all contract tests.

There is no aliasing layer; the rename is a single mechanical
pass. (If alias support becomes necessary, add an `aliases` map
in a follow-up spec.)

## Common pitfalls

- **`guide_url` set to `None` on a citable rule**: the
  contract test fails. Either populate `guide_url` or move
  the rule to a tool-side category.
- **`guide_section` set to `""`**: the contract test fails.
  Use `"internal"` for tool-side rules.
- **A `guide_url` that does not match `index.json`**: the
  resolution test fails. Always sync the URL through
  `index.json::sections[guide_section]`.
- **Adding `guide_section` without updating goldens**: every
  renderer's golden fixtures gain new bytes. Regenerate
  goldens via the per-renderer `--update` flag (or hand-
  apply the diff).
- **Hard-coding URLs in the renderer**: never. The renderer
  always reads `Rule.guide_url`; that field reads from the
  catalogue, which is sourced from `index.json`.

## Validating the index file by hand

```sh
python -c '
import json
idx = json.load(open("docs/jss-guide/index.json"))
for sec, url in idx["sections"].items():
    assert url.startswith("https://"), (sec, url)
print(len(idx["sections"]), "sections OK")
'
```
