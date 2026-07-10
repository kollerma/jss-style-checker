//! Per-document lint-result cache. Mirrors `texlint/lsp/cache.py`:
//! cache key is `(uri, version)`; replacing the entry on a new version
//! is the only invalidation path.

use jsslint_core::report::Violation;
use std::collections::HashMap;

pub struct CachedDocument {
    pub version: i32,
    pub violations: Vec<Violation>,
}

#[derive(Default)]
pub struct DocumentCache {
    by_uri: HashMap<String, CachedDocument>,
}

impl DocumentCache {
    pub fn get(&self, uri: &str) -> Option<&CachedDocument> {
        self.by_uri.get(uri)
    }

    pub fn put(&mut self, uri: String, version: i32, violations: Vec<Violation>) {
        self.by_uri.insert(
            uri,
            CachedDocument {
                version,
                violations,
            },
        );
    }

    pub fn evict(&mut self, uri: &str) {
        self.by_uri.remove(uri);
    }

    pub fn open_uris(&self) -> Vec<String> {
        self.by_uri.keys().cloned().collect()
    }

    /// True iff a cached entry for `uri` exists and matches `version`
    /// exactly. Mirrors `cache.py::DocumentCache.is_current`.
    pub fn is_current(&self, uri: &str, version: i32) -> bool {
        self.by_uri.get(uri).is_some_and(|e| e.version == version)
    }
}
