// Spec 014 — PR-review payload runner for the JSS Style Checker
// composite action. Run via `actions/github-script@v7`. Reads the
// SARIF output produced by the lint step, dismisses any prior
// `jss-lint` review on the PR, and posts one batched COMMENT review
// with one inline comment per violation.
//
// Limits: GitHub allows at most 750 inline comments per review. When
// the SARIF has more, the first 750 are posted inline and a top-level
// review body says "Showing 750 of N; see Security tab for the full
// list."

const fs = require("fs");

const PER_REVIEW_LIMIT = 750;

async function dismissPriorReviews({ github, context }) {
  const { owner, repo } = context.repo;
  const pull_number = context.payload.pull_request.number;
  const reviews = await github.rest.pulls.listReviews({
    owner,
    repo,
    pull_number,
  });
  for (const r of reviews.data) {
    const isBot =
      r.user && r.user.login && r.user.login.endsWith("[bot]");
    const looksLikeOurs =
      (r.body || "").toLowerCase().includes("jss-lint");
    if (isBot && looksLikeOurs && r.state !== "DISMISSED") {
      try {
        await github.rest.pulls.dismissReview({
          owner,
          repo,
          pull_number,
          review_id: r.id,
          message: "outdated",
        });
      } catch (e) {
        // ignore — dismissal can race with state transitions.
      }
    }
  }
}

function sarifResultsToComments(sarif) {
  const run = (sarif.runs && sarif.runs[0]) || {};
  const ruleIndex = {};
  for (const r of (run.tool && run.tool.driver && run.tool.driver.rules) || []) {
    ruleIndex[r.id] = r;
  }
  const out = [];
  for (const r of run.results || []) {
    const loc = r.locations && r.locations[0] && r.locations[0].physicalLocation;
    if (!loc) continue;
    const path = loc.artifactLocation && loc.artifactLocation.uri;
    const region = loc.region || {};
    const line = region.startLine || 1;
    const ruleId = r.ruleId;
    const ruleMeta = ruleIndex[ruleId] || {};
    const helpUri = ruleMeta.helpUri;
    let body = `**${ruleId}**: ${(r.message && r.message.text) || ""}`;
    if (helpUri) {
      body += `\n[(see JSS guide)](${helpUri})`;
    }
    out.push({ path, line, body });
  }
  return out;
}

async function postReview({ github, context, sarifPath }) {
  if (!fs.existsSync(sarifPath)) {
    return;
  }
  if (!context.payload || !context.payload.pull_request) {
    return; // not a PR event
  }
  const sarif = JSON.parse(fs.readFileSync(sarifPath, "utf-8"));
  let comments = sarifResultsToComments(sarif);
  let body = "";
  if (comments.length > PER_REVIEW_LIMIT) {
    body =
      `Showing ${PER_REVIEW_LIMIT} of ${comments.length} jss-lint ` +
      `violations; see the Security tab for the full list.`;
    comments = comments.slice(0, PER_REVIEW_LIMIT);
  } else if (comments.length === 0) {
    return; // nothing to say
  }

  await dismissPriorReviews({ github, context });

  const { owner, repo } = context.repo;
  const pull_number = context.payload.pull_request.number;
  await github.rest.pulls.createReview({
    owner,
    repo,
    pull_number,
    event: "COMMENT",
    body,
    comments,
  });
}

module.exports = { postReview };
