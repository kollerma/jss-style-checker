//! DOI resolution logic — mirrors `texlint/crossref.py`'s matching
//! algorithm exactly (title/surname/year normalization, the Crossref
//! ranking loop, the CRAN `@Manual` → `10.32614/CRAN.package.NAME`
//! shortcut). Generic over [`HttpClient`] so `resolve_doi` (and the
//! unit tests below) never depend on `UreqClient`/the network — only
//! [`make_resolver`], the crate's one public entry point, wires the
//! real client in.

use crate::http::HttpClient;
use jsslint_core::config::DoiResolver;
use regex::Regex;
use serde_json::Value;
use std::collections::HashMap;
use std::sync::{Arc, LazyLock};
use std::time::Duration;

const CROSSREF_URL: &str = "https://api.crossref.org/works";
const DOI_RESOLVER_URL: &str = "https://doi.org/";

/// Mirrors `crossref.py::_DEFAULT_TIMEOUT`.
pub const DEFAULT_TIMEOUT: Duration = Duration::from_secs(8);

/// Minimum title similarity (0..1) to accept a Crossref hit as the
/// same work. Mirrors `crossref.py::_MIN_TITLE_SCORE` — deliberately
/// strict: a wrong DOI is worse than none.
const MIN_TITLE_SCORE: f32 = 0.90;

/// `url = {https://CRAN.R-project.org/package=mfbvar}` -> `mfbvar`.
/// Mirrors `crossref.py::_CRAN_PKG_RE` (note: NOT case-insensitive —
/// only these two exact casings match, same as Python).
static CRAN_PKG_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?:CRAN\.R-project\.org|cran\.r-project\.org)/package[=/]([A-Za-z0-9.]+)").unwrap()
});

static YEAR_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\d{4}").unwrap());
static BRACE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[{}]").unwrap());
static MACRO_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\\[A-Za-z]+").unwrap());
static AND_SPLIT_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\s+and\s+").unwrap());

/// Options for [`make_resolver`]. Mirrors `crossref.py::make_resolver`'s
/// `timeout`/`mailto` keyword args.
#[derive(Debug, Clone)]
pub struct CrossrefOptions {
    pub timeout: Duration,
    pub mailto: Option<String>,
}

impl Default for CrossrefOptions {
    fn default() -> Self {
        Self {
            timeout: DEFAULT_TIMEOUT,
            mailto: None,
        }
    }
}

/// Builds the real, network-backed `jsslint_core::config::DoiResolver`
/// the CLI injects into `ToolConfig` for `jss-lint --crossref`. This is
/// the only function in this crate that touches `UreqClient` — every
/// other function here takes `&dyn HttpClient` so it can be tested
/// hermetically (see this module's `tests`).
pub fn make_resolver(opts: CrossrefOptions) -> Arc<DoiResolver> {
    let client: Arc<dyn HttpClient> = Arc::new(crate::http::UreqClient::new(opts.timeout));
    let mailto = opts.mailto;
    let resolver: Arc<DoiResolver> =
        Arc::new(move |fields: &HashMap<String, String>, entry_type: &str| {
            resolve_doi(client.as_ref(), fields, entry_type, mailto.as_deref())
        });
    resolver
}

/// Mirrors `crossref.py::resolve_doi`. `fields` is a lowercase-keyed
/// field map (title/author/year/url…); `entry_type` is the lowercase
/// BibTeX entry type.
pub fn resolve_doi(
    client: &dyn HttpClient,
    fields: &HashMap<String, String>,
    entry_type: &str,
    mailto: Option<&str>,
) -> Option<String> {
    if entry_type.eq_ignore_ascii_case("manual") {
        return cran_manual_doi(client, fields);
    }
    crossref_doi(
        client,
        fields.get("title").map(String::as_str).unwrap_or(""),
        fields.get("author").map(String::as_str).unwrap_or(""),
        fields.get("year").map(String::as_str).unwrap_or(""),
        mailto,
    )
}

/// Mirrors `crossref.py::_user_agent`. Named for this port's own
/// binary (`jsslint`, not Python's `jss-lint`) — the polite-pool
/// contract only cares that a stable, identifiable, mailto-bearing
/// value is sent, not the exact string.
fn user_agent(mailto: Option<&str>) -> String {
    let base = "jsslint (https://github.com/kollerma/jss-style-checker)";
    match mailto {
        Some(m) if !m.is_empty() => format!("{base}; mailto:{m}"),
        _ => base.to_string(),
    }
}

/// Mirrors `crossref.py::_norm_title`: strip LaTeX braces/commands and
/// collapse whitespace for comparison.
fn norm_title(text: &str) -> String {
    let no_braces = BRACE_RE.replace_all(text, "");
    let no_macros = MACRO_RE.replace_all(&no_braces, " ");
    no_macros
        .to_lowercase()
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
}

/// Mirrors `crossref.py::_year4`.
fn year4(text: &str) -> String {
    YEAR_RE
        .find(text)
        .map(|m| m.as_str().to_string())
        .unwrap_or_default()
}

/// Best-effort first-author surname from a BibTeX `author` field.
/// Mirrors `crossref.py::_first_surname`.
fn first_surname(author: &str) -> String {
    let first = AND_SPLIT_RE.splitn(author, 2).next().unwrap_or("").trim();
    if first.is_empty() {
        return String::new();
    }
    let surname = if first.contains(',') {
        first.split(',').next().unwrap_or("")
    } else {
        first.split_whitespace().last().unwrap_or("")
    };
    BRACE_RE.replace_all(surname, "").to_lowercase()
}

/// A JSON scalar rendered the way Python's `str()` would (used for
/// Crossref's `date-parts` year, always a JSON integer in practice).
fn value_to_plain_string(v: &Value) -> String {
    match v {
        Value::String(s) => s.clone(),
        Value::Number(n) => n.to_string(),
        other => other.to_string(),
    }
}

/// Mirrors `crossref.py::_item_year`.
fn item_year(item: &Value) -> String {
    for key in ["issued", "published", "published-print", "published-online"] {
        let Some(first) = item
            .get(key)
            .and_then(|v| v.get("date-parts"))
            .and_then(|v| v.as_array())
            .and_then(|parts| parts.first())
            .and_then(|part| part.as_array())
            .and_then(|part| part.first())
        else {
            continue;
        };
        return value_to_plain_string(first);
    }
    String::new()
}

/// Mirrors `crossref.py::_item_has_surname`.
fn item_has_surname(item: &Value, surname: &str) -> bool {
    let Some(authors) = item.get("author").and_then(|v| v.as_array()) else {
        return false;
    };
    authors.iter().any(|a| {
        let family = a.get("family").and_then(|v| v.as_str()).unwrap_or("");
        BRACE_RE
            .replace_all(family, "")
            .to_lowercase()
            .contains(surname)
    })
}

/// Ratio (0..1) via `difflib`'s `SequenceMatcher`, char-sequenced (not
/// byte-sequenced) so non-ASCII titles compare the same way Python's
/// `SequenceMatcher` (always char-sequenced) does.
fn title_ratio(a: &str, b: &str) -> f32 {
    let ca: Vec<char> = a.chars().collect();
    let cb: Vec<char> = b.chars().collect();
    let mut matcher = difflib::sequencematcher::SequenceMatcher::new(&ca, &cb);
    matcher.ratio()
}

/// `application/x-www-form-urlencoded` percent-encoding matching
/// `urllib.parse.urlencode`'s default `quote_via=quote_plus` (spaces
/// -> `+`, unreserved chars `A-Za-z0-9-_.~` untouched).
fn quote_plus(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for &b in s.as_bytes() {
        match b {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                out.push(b as char)
            }
            b' ' => out.push('+'),
            _ => out.push_str(&format!("%{b:02X}")),
        }
    }
    out
}

/// Mirrors `urllib.parse.quote(doi, safe="/.:")`.
fn quote_doi(doi: &str) -> String {
    let mut out = String::with_capacity(doi.len());
    for &b in doi.as_bytes() {
        match b {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' | b'/' | b':' => {
                out.push(b as char)
            }
            _ => out.push_str(&format!("%{b:02X}")),
        }
    }
    out
}

/// Mirrors `crossref.py::_crossref_doi`: query by bibliographic title
/// (biased with author, when known) and accept the top-scoring hit
/// only when its title is a close match and it doesn't contradict a
/// *known* year or first-author surname.
fn crossref_doi(
    client: &dyn HttpClient,
    title: &str,
    author: &str,
    year: &str,
    mailto: Option<&str>,
) -> Option<String> {
    let title = title.trim();
    if title.is_empty() {
        return None;
    }
    let want = norm_title(title);
    let want_year = year4(year);
    let want_surname = first_surname(author);

    let mut query = format!("query.bibliographic={}&rows=10", quote_plus(&want));
    if !want_surname.is_empty() {
        query.push_str("&query.author=");
        query.push_str(&quote_plus(&want_surname));
    }
    let url = format!("{CROSSREF_URL}?{query}");
    let data = client.get_json(&url, &user_agent(mailto))?;

    let items = data
        .get("message")
        .and_then(|m| m.get("items"))
        .and_then(|i| i.as_array())?;

    let mut best_doi: Option<String> = None;
    let mut best_score = -1.0f32;
    for item in items {
        let Some(titles) = item
            .get("title")
            .and_then(|t| t.as_array())
            .filter(|a| !a.is_empty())
        else {
            continue;
        };
        let Some(doi) = item
            .get("DOI")
            .and_then(|d| d.as_str())
            .filter(|s| !s.is_empty())
        else {
            continue;
        };
        let Some(first_title) = titles.first().and_then(|t| t.as_str()) else {
            continue;
        };
        let tscore = title_ratio(&want, &norm_title(first_title));
        if tscore < MIN_TITLE_SCORE {
            continue;
        }
        // Disambiguate same-title works by year and first-author
        // surname: a mismatch on a *known* year or author rejects the
        // candidate, so a wrong DOI is never written.
        let iyear = item_year(item);
        if !want_year.is_empty() && !iyear.is_empty() && iyear != want_year {
            continue;
        }
        let has_author_field = item
            .get("author")
            .and_then(|a| a.as_array())
            .is_some_and(|a| !a.is_empty());
        if !want_surname.is_empty() && has_author_field && !item_has_surname(item, &want_surname) {
            continue;
        }
        let mut score = tscore;
        if !want_year.is_empty() && iyear == want_year {
            score += 0.1;
        }
        if !want_surname.is_empty() && item_has_surname(item, &want_surname) {
            score += 0.1;
        }
        if score > best_score {
            best_score = score;
            best_doi = Some(doi.to_string());
        }
    }
    best_doi
}

/// Mirrors `crossref.py::_doi_resolves`: confirm a candidate DOI
/// actually resolves via `doi.org` (no `mailto` — same as Python,
/// which doesn't thread `mailto` through this call either).
fn doi_resolves(client: &dyn HttpClient, doi: &str) -> bool {
    let url = format!("{DOI_RESOLVER_URL}{}", quote_doi(doi));
    client.head_ok(&url, &user_agent(None))
}

/// Mirrors `crossref.py::_cran_manual_doi`.
fn cran_manual_doi(client: &dyn HttpClient, fields: &HashMap<String, String>) -> Option<String> {
    for key in ["url", "note", "howpublished"] {
        let Some(value) = fields.get(key) else {
            continue;
        };
        let Some(caps) = CRAN_PKG_RE.captures(value) else {
            continue;
        };
        let pkg = caps.get(1).unwrap().as_str();
        let doi = format!("10.32614/CRAN.package.{pkg}");
        return if doi_resolves(client, &doi) {
            Some(doi)
        } else {
            None
        };
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::sync::Mutex;

    /// Mirrors the Python tests' `opener` seam: a canned JSON body for
    /// GET, a canned bool for HEAD, both independent of the requested
    /// URL (same as `_crossref_opener` returning the same payload
    /// regardless of `req`). Also records every `User-Agent` sent, so
    /// `mailto` wiring can be asserted on.
    #[derive(Default)]
    struct MockClient {
        get_response: Option<Value>,
        head_response: bool,
        seen_user_agents: Mutex<Vec<String>>,
    }

    impl HttpClient for MockClient {
        fn get_json(&self, _url: &str, user_agent: &str) -> Option<Value> {
            self.seen_user_agents
                .lock()
                .unwrap()
                .push(user_agent.to_string());
            self.get_response.clone()
        }

        fn head_ok(&self, _url: &str, user_agent: &str) -> bool {
            self.seen_user_agents
                .lock()
                .unwrap()
                .push(user_agent.to_string());
            self.head_response
        }
    }

    struct FailingClient;
    impl HttpClient for FailingClient {
        fn get_json(&self, _url: &str, _user_agent: &str) -> Option<Value> {
            None
        }
        fn head_ok(&self, _url: &str, _user_agent: &str) -> bool {
            false
        }
    }

    fn crossref_item(title: &str, doi: &str, family: &str, year: i64) -> Value {
        json!({
            "title": [title],
            "DOI": doi,
            "author": [{"family": family}],
            "issued": {"date-parts": [[year]]},
        })
    }

    fn fields(pairs: &[(&str, &str)]) -> HashMap<String, String> {
        pairs
            .iter()
            .map(|(k, v)| (k.to_string(), v.to_string()))
            .collect()
    }

    fn crossref_client(items: Vec<Value>) -> MockClient {
        MockClient {
            get_response: Some(json!({"message": {"items": items}})),
            head_response: false,
            seen_user_agents: Mutex::new(Vec::new()),
        }
    }

    #[test]
    fn exact_title_match_returns_doi() {
        let client = crossref_client(vec![crossref_item(
            "A Study of Things",
            "10.1/aaa",
            "Smith",
            2020,
        )]);
        let doi = resolve_doi(
            &client,
            &fields(&[
                ("title", "A Study of Things"),
                ("author", "Smith"),
                ("year", "2020"),
            ]),
            "article",
            None,
        );
        assert_eq!(doi.as_deref(), Some("10.1/aaa"));
    }

    #[test]
    fn low_title_similarity_returns_none() {
        let client = crossref_client(vec![crossref_item(
            "Totally Unrelated Work",
            "10.1/bbb",
            "Smith",
            2020,
        )]);
        let doi = resolve_doi(
            &client,
            &fields(&[
                ("title", "A Study of Things"),
                ("author", "Smith"),
                ("year", "2020"),
            ]),
            "article",
            None,
        );
        assert_eq!(doi, None);
    }

    #[test]
    fn year_mismatch_rejected() {
        let client = crossref_client(vec![crossref_item(
            "A Study of Things",
            "10.1/ccc",
            "Smith",
            1999,
        )]);
        let doi = resolve_doi(
            &client,
            &fields(&[
                ("title", "A Study of Things"),
                ("author", "Smith"),
                ("year", "2020"),
            ]),
            "article",
            None,
        );
        assert_eq!(doi, None);
    }

    #[test]
    fn author_mismatch_rejected() {
        let client = crossref_client(vec![crossref_item(
            "A Study of Things",
            "10.1/ddd",
            "Jones",
            2020,
        )]);
        let doi = resolve_doi(
            &client,
            &fields(&[
                ("title", "A Study of Things"),
                ("author", "Smith"),
                ("year", "2020"),
            ]),
            "article",
            None,
        );
        assert_eq!(doi, None);
    }

    #[test]
    fn prefers_year_and_author_match_over_bare_title() {
        let client = crossref_client(vec![
            crossref_item("A Study of Things", "10.1/wrong", "Jones", 1990),
            crossref_item("A Study of Things", "10.1/right", "Smith", 2020),
        ]);
        let doi = resolve_doi(
            &client,
            &fields(&[
                ("title", "A Study of Things"),
                ("author", "Smith, John"),
                ("year", "2020"),
            ]),
            "article",
            None,
        );
        assert_eq!(doi.as_deref(), Some("10.1/right"));
    }

    #[test]
    fn empty_title_returns_none() {
        let client = crossref_client(vec![]);
        let doi = resolve_doi(&client, &fields(&[("title", "")]), "article", None);
        assert_eq!(doi, None);
    }

    #[test]
    fn network_error_returns_none() {
        let doi = resolve_doi(
            &FailingClient,
            &fields(&[("title", "X Y Z")]),
            "article",
            None,
        );
        assert_eq!(doi, None);
    }

    #[test]
    fn malformed_json_shape_returns_none() {
        // `get_json` itself already collapses parse errors to `None`
        // (see `UreqClient`/tests below); this exercises the
        // "well-formed JSON, wrong shape" half of the same contract.
        let client = MockClient {
            get_response: Some(json!({"unexpected": "shape"})),
            head_response: false,
            seen_user_agents: Mutex::new(Vec::new()),
        };
        let doi = resolve_doi(&client, &fields(&[("title", "X Y Z")]), "article", None);
        assert_eq!(doi, None);
    }

    #[test]
    fn cran_manual_doi_when_resolvable() {
        let client = MockClient {
            get_response: None,
            head_response: true,
            seen_user_agents: Mutex::new(Vec::new()),
        };
        let doi = resolve_doi(
            &client,
            &fields(&[("url", "https://CRAN.R-project.org/package=mfbvar")]),
            "manual",
            None,
        );
        assert_eq!(doi.as_deref(), Some("10.32614/CRAN.package.mfbvar"));
    }

    #[test]
    fn cran_manual_none_when_unresolvable() {
        let client = MockClient {
            get_response: None,
            head_response: false,
            seen_user_agents: Mutex::new(Vec::new()),
        };
        let doi = resolve_doi(
            &client,
            &fields(&[("url", "https://CRAN.R-project.org/package=mfbvar")]),
            "manual",
            None,
        );
        assert_eq!(doi, None);
    }

    #[test]
    fn non_cran_manual_returns_none() {
        let doi = resolve_doi(
            &FailingClient,
            &fields(&[("url", "https://example.org/thing")]),
            "manual",
            None,
        );
        assert_eq!(doi, None);
    }

    #[test]
    fn mailto_reaches_the_user_agent() {
        let client = crossref_client(vec![crossref_item(
            "A Study of Things",
            "10.1/eee",
            "Smith",
            2020,
        )]);
        let doi = resolve_doi(
            &client,
            &fields(&[
                ("title", "A Study of Things"),
                ("author", "Smith"),
                ("year", "2020"),
            ]),
            "article",
            Some("a@b.c"),
        );
        assert_eq!(doi.as_deref(), Some("10.1/eee"));
        let seen = client.seen_user_agents.lock().unwrap();
        assert!(seen.iter().any(|ua| ua.contains("mailto:a@b.c")));
    }

    #[test]
    fn no_mailto_omits_it_from_the_user_agent() {
        let client = crossref_client(vec![]);
        let _ = resolve_doi(&client, &fields(&[("title", "X Y Z")]), "article", None);
        let seen = client.seen_user_agents.lock().unwrap();
        assert!(seen.iter().all(|ua| !ua.contains("mailto")));
    }

    #[test]
    fn norm_title_strips_braces_and_macros() {
        // Braces strip first, so `\pkg{Study}` becomes `\pkgStudy` before
        // the macro regex runs — `\[A-Za-z]+` then greedily eats
        // "Study" too (no boundary between the macro name and the
        // brace-stripped argument). Confirmed against
        // `texlint.crossref._norm_title` — a faithfully-ported quirk,
        // not a bug: exact title-similarity parity depends on both
        // sides losing "Study" the same way.
        assert_eq!(norm_title(r"{A} \pkg{Study} of  Things"), "a of things");
        assert_eq!(norm_title("{Multiple}   spaces"), "multiple spaces");
        assert_eq!(norm_title(r"A \emph{plain} title"), "a title");
    }

    #[test]
    fn first_surname_handles_family_comma_given_and_bare_form() {
        assert_eq!(first_surname("Breiman, Leo"), "breiman");
        assert_eq!(first_surname("Leo Breiman"), "breiman");
        assert_eq!(first_surname("Breiman, Leo and Cutler, Adele"), "breiman");
        assert_eq!(first_surname(""), "");
    }

    #[test]
    fn quote_plus_matches_urlencode_semantics() {
        assert_eq!(quote_plus("a b"), "a+b");
        assert_eq!(quote_plus("a&b=c"), "a%26b%3Dc");
    }

    #[test]
    fn quote_doi_keeps_slash_and_colon_unescaped() {
        assert_eq!(
            quote_doi("10.32614/CRAN.package.mfbvar"),
            "10.32614/CRAN.package.mfbvar"
        );
        assert_eq!(quote_doi("10.1/a b"), "10.1/a%20b");
    }
}
