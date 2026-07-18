//! Blocking HTTP transport for Crossref/CRAN lookups, behind an
//! injectable trait — mirrors `crossref.py`'s `opener` seam (the
//! parameter that lets tests replace `urllib.request.urlopen`) so
//! `resolve.rs`'s tests can supply recorded/mock responses instead of
//! hitting the network. [`UreqClient`] is the only thing in this whole
//! crate that actually opens a socket.

use std::time::Duration;

/// A GET-as-JSON or HEAD-as-exists request, reduced to what
/// `resolve.rs` needs. Every network, timeout, decode, or non-2xx/3xx
/// status outcome collapses to `None`/`false` — mirrors
/// `crossref.py::_http_json`/`_doi_resolves`'s "any error -> treat as
/// absent" contract (a wrong DOI is worse than a missed one, and a
/// network hiccup must never fail the lint run).
pub trait HttpClient: Send + Sync {
    /// GET `url` with the given `User-Agent`, parsed as JSON.
    fn get_json(&self, url: &str, user_agent: &str) -> Option<serde_json::Value>;

    /// HEAD `url` with the given `User-Agent`; `true` iff the response
    /// is a success (2xx/3xx, i.e. not a `ureq` error).
    fn head_ok(&self, url: &str, user_agent: &str) -> bool;
}

/// Real network client: `ureq`, pure-Rust, blocking, rustls (no
/// OpenSSL/native-tls in the dependency graph) — see this crate's
/// `Cargo.toml`.
pub struct UreqClient {
    agent: ureq::Agent,
}

impl UreqClient {
    pub fn new(timeout: Duration) -> Self {
        let config = ureq::Agent::config_builder()
            .timeout_global(Some(timeout))
            .build();
        Self {
            agent: config.into(),
        }
    }
}

impl HttpClient for UreqClient {
    fn get_json(&self, url: &str, user_agent: &str) -> Option<serde_json::Value> {
        let mut resp = self
            .agent
            .get(url)
            .header("User-Agent", user_agent)
            .call()
            .ok()?;
        let body = resp.body_mut().read_to_string().ok()?;
        serde_json::from_str(&body).ok()
    }

    fn head_ok(&self, url: &str, user_agent: &str) -> bool {
        // With `http_status_as_error` at its default (true), `Ok(_)`
        // only ever carries a 2xx/3xx response — 4xx/5xx surface as
        // `Err(Error::StatusCode(_))`, which the `false` fallthrough
        // below already covers.
        self.agent
            .head(url)
            .header("User-Agent", user_agent)
            .call()
            .is_ok()
    }
}
