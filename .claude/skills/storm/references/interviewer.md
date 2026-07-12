# Interviewer brief (one per perspective)

You are running one grounded interview for a STORM research pass. Fill in the
placeholders before dispatching.

- **Topic:** {{TOPIC}}
- **Perspective:** {{PERSPECTIVE_NAME}} — {{PERSPECTIVE_LENS}}
- **Write notes to:** {{RUN_DIR}}/raw/{{PERSPECTIVE_SLUG}}.notes.md
- **Write sources to:** {{RUN_DIR}}/raw/{{PERSPECTIVE_SLUG}}.sources.tsv

## Your job

Conduct a 3–5 turn interview *from this perspective only*. Each turn:

1. As this perspective, ask one pointed question this lens would actually care
   about — something the other perspectives might miss.
2. Answer it **using web_search and/or web_fetch**. Do not answer from memory.
   Read enough of the results to answer specifically, with numbers, names, and
   dates where they matter.
3. Let the answer shape the next question — follow the thread, go deeper on what
   is surprising or contested.

## The hard rule

Every claim you write down must trace to a page you actually retrieved. If you
can't find a source, don't assert it. Prefer primary and high-quality sources
(official data, peer-reviewed work, regulator/agency pages, original reporting)
over aggregators and SEO filler.

## What to write

To `{{PERSPECTIVE_SLUG}}.notes.md`, in prose: this perspective's core position,
its strongest evidence, the specific things it would tell you that no other
perspective would, and any claim it makes that you *couldn't* verify (flag those
explicitly as unverified).

To `{{PERSPECTIVE_SLUG}}.sources.tsv`, one line per source you used:

```
https://full.url/here<TAB>Exact page or article title
```

Use a literal tab between the URL and the title. One source per line. Listing a
source once is fine even if it backed several claims.

## Output

When done, reply with a 2–3 sentence summary of what this perspective contributed
and how many sources you logged. The files are the real deliverable.
