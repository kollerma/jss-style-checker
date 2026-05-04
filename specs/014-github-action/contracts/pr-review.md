# Contract: PR-Review Posting

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

This contract documents the behaviour of
`action/scripts/post-review.js`, executed by
`actions/github-script@v7` when the Action runs on a
`pull_request` event.

## C-1 One review per workflow run

The script MUST POST exactly one review:
`POST /repos/{owner}/{repo}/pulls/{number}/reviews` with
`event = "COMMENT"` and `comments[]` populated from the
SARIF results.

## C-2 Comment shape

Each entry in `comments[]`:

| Field      | Source                                                         |
| ---------- | -------------------------------------------------------------- |
| `path`     | `result.locations[0].physicalLocation.artifactLocation.uri`    |
| `line`     | `result.locations[0].physicalLocation.region.startLine`        |
| `body`     | per-line markdown: rule id (bold), message, link to guide URL  |
| `side`     | `RIGHT` (default; comments on the new file)                    |

`body` template:

```
**<RULE-ID>**: <message>
[(see <guide_section>)](<guide_url>)
```

When `guide_url` is absent (sentinel rules), the link line
is omitted.

## C-3 Comment limit

GitHub's per-review limit is 750 inline comments. If the
SARIF has more than 750 results, the script:
- Includes the first 750 in `comments[]`.
- Adds a top-level review `body` text:
  `Showing 750 of N violations; see Security tab for the
  full list.`

The Security tab (SARIF) carries the full list regardless.

## C-4 Stale-comment dismissal

Before posting, the script MUST:

1. List existing reviews:
   `GET /repos/{o}/{r}/pulls/{n}/reviews`.
2. Filter to those whose `user.login` ends in `[bot]` AND
   whose `body` or first comment mentions `jss-lint`
   (i.e., authored by this Action, not other bots).
3. For each match, dismiss via the GraphQL
   `dismissPullRequestReview` mutation with
   `dismissalReason: "outdated"`.

Dismissal happens BEFORE the new review is posted so the
PR conversation does not show two active "jss-lint"
reviews simultaneously.

## C-5 No state outside the API

The script MUST NOT write to the filesystem (except
reading the SARIF input). It MUST NOT cache state across
runs. Idempotency relies entirely on C-4's dismissal
step.

## C-6 Error handling

Network or API errors:
- Are logged to the Action log via `core.warning(...)`.
- Do NOT fail the workflow run if `fail-on-severity`
  evaluates to 0 ("the lint succeeded; commenting is
  best-effort").
- DO fail the run if `fail-on-severity` already
  evaluates to 1 (the lint already wants to fail; the
  comment failure is informational only).

## C-7 Bot-author identity

The script consumes `context.actor` to identify the
workflow's author. For `github-actions[bot]`-driven
runs (the default), this is the dismissal target. For
custom-bot runs (PAT-driven), the user MUST configure the
bot's login string matches the dismissal filter — out of
scope for v1, documented in the Action README.

## C-8 No PR-comment fall-back inside this script

When `comment-mode == 'pr-comment'` (not `pr-review`), a
DIFFERENT script (or a separate composite step) handles
the PR-comment surface. `post-review.js` is responsible
ONLY for the `pr-review` mode.
