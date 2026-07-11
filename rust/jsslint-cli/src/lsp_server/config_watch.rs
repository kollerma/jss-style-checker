//! `.jss-lint.toml` + client-settings state for the LSP server. Mirrors
//! `texlint/lsp/config_watch.py`.

use jsslint_core::config::{RawOverrides, ToolConfig};
use jsslint_core::report::Severity;
use serde_json::Value;
use std::collections::HashSet;
use std::path::{Path, PathBuf};

pub struct ConfigState {
    pub path: Option<PathBuf>,
    pub cfg: ToolConfig,
    pub last_error: Option<String>,
    /// Raw `jssStyleChecker` section from the latest
    /// `workspace/didChangeConfiguration` push.
    pub client_settings: Value,
    /// `"change"` (default) or `"save"` — gates whether `didChange`
    /// lints or only `didSave`/`didOpen` do.
    pub run_on: String,
}

impl Default for ConfigState {
    fn default() -> Self {
        Self {
            path: None,
            cfg: ToolConfig::default(),
            last_error: None,
            client_settings: Value::Object(serde_json::Map::new()),
            run_on: "change".to_string(),
        }
    }
}

impl ConfigState {
    /// The config rules actually run with: `.jss-lint.toml` as the
    /// base, client settings layered on top.
    pub fn effective(&self) -> ToolConfig {
        merge_client_settings(&self.cfg, &self.client_settings)
    }
}

fn normalize_ignore_rules_value(v: &Value) -> HashSet<String> {
    match v {
        Value::String(s) => s
            .split(',')
            .map(|p| p.trim().to_string())
            .filter(|p| !p.is_empty())
            .collect(),
        Value::Array(items) => items
            .iter()
            .filter_map(Value::as_str)
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect(),
        _ => HashSet::new(),
    }
}

fn normalize_severity_overrides_value(
    obj: &serde_json::Map<String, Value>,
) -> Vec<(String, Severity)> {
    obj.iter()
        .filter_map(|(k, v)| {
            let sev = Severity::parse(&v.as_str()?.to_lowercase())?;
            Some((k.trim().to_uppercase(), sev))
        })
        .collect()
}

/// Layers the client's `jssStyleChecker` settings over `cfg`.
/// Precedence is additive, never wholesale (VS Code pushes its
/// defaults for every key on every change, so "client replaces file"
/// would silently erase `.jss-lint.toml` values): `ignoreRules`
/// **unions** into `ignore_rules`; `severityOverrides` **dict-updates**
/// over file overrides (client wins per rule id); `codeWidth` replaces
/// `code_width`. Mirrors `config_watch.py::merge_client_settings`.
pub fn merge_client_settings(cfg: &ToolConfig, settings: &Value) -> ToolConfig {
    let mut out = cfg.clone();
    let Some(obj) = settings.as_object() else {
        return out;
    };
    if obj.is_empty() {
        return out;
    }
    if let Some(v) = obj.get("ignoreRules") {
        let extra = normalize_ignore_rules_value(v);
        if !extra.is_empty() {
            out.ignore_rules.extend(extra);
        }
    }
    if let Some(v) = obj.get("severityOverrides").and_then(Value::as_object) {
        let client_overrides = normalize_severity_overrides_value(v);
        if !client_overrides.is_empty() {
            for (rule_id, sev) in client_overrides {
                out.severity_overrides.insert(rule_id, sev);
            }
        }
    }
    if let Some(n) = obj.get("codeWidth").and_then(Value::as_f64) {
        if n > 0.0 {
            out.code_width = n as u32;
        }
    }
    out
}

/// Reloads the config from `path`. Returns `true` when the new config
/// replaces the old; `false` when the file is malformed (the previous
/// config stays active). Mirrors `config_watch.py::reload`.
pub fn reload(state: &mut ConfigState, path: &Path, mut log: impl FnMut(&str)) -> bool {
    let text = match std::fs::read_to_string(path) {
        Ok(t) => t,
        Err(exc) => {
            let msg = format!("failed to read {}: {exc}", path.display());
            log(&msg);
            state.last_error = Some(msg);
            return false;
        }
    };
    if let Err(exc) = text.parse::<toml::Table>() {
        let msg = format!("failed to read {}: {exc}", path.display());
        log(&msg);
        state.last_error = Some(msg);
        return false;
    }

    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    let new_cfg = jsslint_core::config::load(parent, &RawOverrides::default());
    state.path = Some(path.to_path_buf());
    state.cfg = new_cfg;
    state.last_error = None;
    true
}
