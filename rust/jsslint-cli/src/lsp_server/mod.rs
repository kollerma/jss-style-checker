//! `jss-lint lsp` — LSP 3.17 server, mirrors `texlint/lsp/server.py`
//! (spec 011). Built on `lsp-server` + `lsp-types` (the
//! rust-analyzer-ecosystem crates: a synchronous, crossbeam-channel-
//! based JSON-RPC scaffold) rather than an async framework — this
//! whole workspace has no async runtime, and a synchronous main loop
//! with a generation-counter debounce (see `schedule_debounced_lint`)
//! covers everything `pygls` gives Python here.
//!
//! Simplifications from the Python reference, all deliberate (see
//! inline comments at each site): full-document sync (not
//! incremental) declared in server capabilities; no dynamic
//! `client/registerCapability` call for file watching (Python doesn't
//! either — it relies on the client registering its own watcher); the
//! `workspace/applyEdit` response (success/failure of the client
//! applying `applyAllFixes`'s edit) isn't correlated back to a log
//! line, since it's a pure logging side effect with no observable
//! protocol behavior.
//!
//! Verification: this is a stateful bidirectional protocol, not a
//! batch CLI command, so it can't be differentially tested by diffing
//! stdout against the Python binary the way every other subcommand in
//! this port is. Instead: the pure Violation/Fix -> Diagnostic/
//! CodeAction projections (`jsslint_core::lsp`) are already
//! differentially validated against `texlint.lsp.conversions`
//! (`lsp_parity.rs`); this module's own tests drive the compiled
//! binary as a real LSP client would (initialize/didOpen/codeAction/
//! shutdown over its actual stdio) and assert on published
//! diagnostics and code actions.

mod cache;
mod config_watch;

use cache::DocumentCache;
use config_watch::ConfigState;
use crossbeam_channel::{unbounded, Receiver, Sender};
use jsslint_core::catalogue;
use jsslint_core::engine::{self, ParsedDocument};
use jsslint_core::report::FixConfidence;
use lsp_server::{Connection, ErrorCode, Message, Notification, Request, RequestId, Response};
use lsp_types::{
    notification::{Notification as _, PublishDiagnostics, ShowMessage},
    request::{ApplyWorkspaceEdit, Request as _},
    ApplyWorkspaceEditParams, CodeAction, CodeActionKind, CodeActionOrCommand, CodeActionParams,
    CodeActionProviderCapability, Diagnostic, DiagnosticSeverity, DidChangeConfigurationParams,
    DidChangeTextDocumentParams, DidChangeWatchedFilesParams, DidCloseTextDocumentParams,
    DidOpenTextDocumentParams, DidSaveTextDocumentParams, ExecuteCommandOptions,
    ExecuteCommandParams, MessageType, Position, PublishDiagnosticsParams, Range,
    ServerCapabilities, ShowMessageParams, TextDocumentSyncCapability, TextDocumentSyncKind,
    TextDocumentSyncOptions, TextEdit, Uri, WorkspaceEdit,
};
use std::collections::HashMap;
use std::path::PathBuf;
use std::process::ExitCode;
use std::time::Duration;

const DEBOUNCE_MS: u64 = 200;
const SUPPORTED_LSP_SUFFIXES: &[&str] = &[".tex", ".ltx", ".bib"];

/// `(uri, generation)` sent when a debounced lint timer fires.
type DebounceMsg = (String, u64);

/// Console entry point for `jss-lint lsp`. Spawns the server on stdio
/// and blocks until the editor closes the connection. Mirrors
/// `server.py::main`.
pub fn main() -> ExitCode {
    let (connection, io_threads) = Connection::stdio();

    let capabilities = ServerCapabilities {
        text_document_sync: Some(TextDocumentSyncCapability::Options(
            TextDocumentSyncOptions {
                open_close: Some(true),
                // Full sync (not incremental): simpler, and the server
                // capability declaration is this port's own choice —
                // Python's pygls-inferred sync kind isn't a byte-parity
                // target here, only the diagnostics content is.
                change: Some(TextDocumentSyncKind::FULL),
                ..Default::default()
            },
        )),
        code_action_provider: Some(CodeActionProviderCapability::Simple(true)),
        execute_command_provider: Some(ExecuteCommandOptions {
            commands: vec!["jss-lint.applyAllFixes".to_string()],
            work_done_progress_options: Default::default(),
        }),
        ..Default::default()
    };
    let capabilities_json = serde_json::to_value(capabilities).expect("capabilities serialize");
    if connection.initialize(capabilities_json).is_err() {
        return ExitCode::from(1);
    }

    run_main_loop(&connection);

    drop(connection);
    let _ = io_threads.join();
    ExitCode::from(0)
}

fn uri_to_path(uri: &str) -> Option<PathBuf> {
    let url = url::Url::parse(uri).ok()?;
    if url.scheme() != "file" {
        return None;
    }
    url.to_file_path().ok()
}

fn is_supported_lsp_path(path: &std::path::Path) -> bool {
    let Some(ext) = path.extension().and_then(|e| e.to_str()) else {
        return false;
    };
    let dotted = format!(".{}", ext.to_lowercase());
    SUPPORTED_LSP_SUFFIXES.contains(&dotted.as_str())
}

fn guide_url_for(rule_id: &str) -> Option<&'static str> {
    catalogue::lookup(rule_id).and_then(|m| m.guide_url)
}

fn to_lsp_position(p: jsslint_core::lsp::Position) -> Position {
    Position {
        line: p.line,
        character: p.character,
    }
}

fn to_lsp_range(r: jsslint_core::lsp::Range) -> Range {
    Range {
        start: to_lsp_position(r.start),
        end: to_lsp_position(r.end),
    }
}

fn to_lsp_diagnostic(d: &jsslint_core::lsp::Diagnostic) -> Diagnostic {
    Diagnostic {
        range: to_lsp_range(d.range),
        severity: Some(match d.severity {
            1 => DiagnosticSeverity::ERROR,
            2 => DiagnosticSeverity::WARNING,
            3 => DiagnosticSeverity::INFORMATION,
            _ => DiagnosticSeverity::HINT,
        }),
        code: Some(lsp_types::NumberOrString::String(d.code.clone())),
        source: Some(d.source.clone()),
        message: d.message.clone(),
        code_description: d
            .code_description_href
            .as_ref()
            .and_then(|h| h.parse::<Uri>().ok())
            .map(|href| lsp_types::CodeDescription { href }),
        ..Default::default()
    }
}

fn to_lsp_text_edit(e: &jsslint_core::lsp::TextEdit) -> TextEdit {
    TextEdit {
        range: to_lsp_range(e.range),
        new_text: e.new_text.clone(),
    }
}

/// One open document's tracked text + version. This server keeps its
/// own copy rather than relying on a framework-managed workspace (no
/// pygls equivalent here).
struct OpenDoc {
    text: String,
    version: i32,
}

struct ServerState {
    docs: HashMap<String, OpenDoc>,
    cache: DocumentCache,
    config: ConfigState,
    /// Debounce generation counter per URI — a fired timer only lints
    /// if its captured generation still matches the URI's current
    /// generation when it wakes up; a newer `didChange` bumping the
    /// generation makes any earlier timer a silent no-op. Achieves the
    /// same effect as `server.py`'s `asyncio` `TimerHandle.cancel()`
    /// without needing an async runtime.
    generations: HashMap<String, u64>,
    next_request_id: i32,
}

impl ServerState {
    fn new() -> Self {
        Self {
            docs: HashMap::new(),
            cache: DocumentCache::default(),
            config: ConfigState::default(),
            generations: HashMap::new(),
            next_request_id: 0,
        }
    }
}

fn publish_diagnostics(connection: &Connection, uri: &str, diagnostics: Vec<Diagnostic>) {
    let Ok(lsp_uri) = uri.parse::<Uri>() else {
        return;
    };
    let params = PublishDiagnosticsParams {
        uri: lsp_uri,
        diagnostics,
        version: None,
    };
    let _ = connection
        .sender
        .send(Message::Notification(Notification::new(
            PublishDiagnostics::METHOD.to_string(),
            params,
        )));
}

/// Synchronously lints `uri` and publishes diagnostics. Mirrors
/// `server.py::_lint_uri`.
fn lint_uri(
    connection: &Connection,
    state: &mut ServerState,
    uri: &str,
    version: i32,
    source: &str,
) {
    let Some(path) = uri_to_path(uri) else {
        return;
    };
    if !is_supported_lsp_path(&path) {
        return;
    }

    let path_str = path.to_string_lossy().into_owned();
    let sources = vec![(path_str, source.to_string())];
    let Ok(document) = ParsedDocument::from_sources(&sources) else {
        return;
    };
    let cfg = state.config.effective();
    if cfg.journal != "jss" {
        return;
    }
    let report = engine::run(&cfg, &document);

    let diagnostics: Vec<Diagnostic> = report
        .violations
        .iter()
        .map(|v| {
            let guide_url = guide_url_for(&v.rule_id);
            let d = jsslint_core::lsp::violation_to_diagnostic(v, guide_url, Some(source));
            to_lsp_diagnostic(&d)
        })
        .collect();

    state.cache.put(uri.to_string(), version, report.violations);
    publish_diagnostics(connection, uri, diagnostics);
}

/// Cancel-by-superseding debounce: spawns a thread that sends a
/// "lint due" message after `DEBOUNCE_MS`, tagged with the URI's
/// current generation. Mirrors `server.py::_schedule_lint`.
fn schedule_debounced_lint(state: &mut ServerState, tx: &Sender<DebounceMsg>, uri: &str) {
    let gen = state.generations.entry(uri.to_string()).or_insert(0);
    *gen += 1;
    let my_gen = *gen;
    let tx = tx.clone();
    let uri = uri.to_string();
    std::thread::spawn(move || {
        std::thread::sleep(Duration::from_millis(DEBOUNCE_MS));
        let _ = tx.send((uri, my_gen));
    });
}

fn relint_open_documents(connection: &Connection, state: &mut ServerState) {
    let uris = state.cache.open_uris();
    for uri in uris {
        if let Some(doc) = state.docs.get(&uri) {
            let (text, version) = (doc.text.clone(), doc.version);
            lint_uri(connection, state, &uri, version, &text);
        }
    }
}

fn handle_notification(
    connection: &Connection,
    state: &mut ServerState,
    debounce_tx: &Sender<DebounceMsg>,
    not: Notification,
) {
    match not.method.as_str() {
        "textDocument/didOpen" => {
            let Ok(params) = serde_json::from_value::<DidOpenTextDocumentParams>(not.params) else {
                return;
            };
            let uri = params.text_document.uri.to_string();
            let text = params.text_document.text;
            let version = params.text_document.version;
            state.docs.insert(
                uri.clone(),
                OpenDoc {
                    text: text.clone(),
                    version,
                },
            );
            // Open documents lint immediately (no debounce).
            lint_uri(connection, state, &uri, version, &text);
        }
        "textDocument/didChange" => {
            let Ok(params) = serde_json::from_value::<DidChangeTextDocumentParams>(not.params)
            else {
                return;
            };
            let uri = params.text_document.uri.to_string();
            let version = params.text_document.version;
            // Full sync only: exactly one content change with the
            // whole new text.
            let Some(text) = params.content_changes.into_iter().next().map(|c| c.text) else {
                return;
            };
            state.docs.insert(
                uri.clone(),
                OpenDoc {
                    text: text.clone(),
                    version,
                },
            );
            if state.config.run_on == "save" {
                return;
            }
            schedule_debounced_lint(state, debounce_tx, &uri);
        }
        "textDocument/didSave" => {
            let Ok(params) = serde_json::from_value::<DidSaveTextDocumentParams>(not.params) else {
                return;
            };
            let uri = params.text_document.uri.to_string();
            if let Some(doc) = state.docs.get(&uri) {
                let (text, version) = (doc.text.clone(), doc.version);
                lint_uri(connection, state, &uri, version, &text);
            }
        }
        "textDocument/didClose" => {
            let Ok(params) = serde_json::from_value::<DidCloseTextDocumentParams>(not.params)
            else {
                return;
            };
            let uri = params.text_document.uri.to_string();
            state.docs.remove(&uri);
            state.cache.evict(&uri);
            publish_diagnostics(connection, &uri, vec![]);
        }
        "workspace/didChangeConfiguration" => {
            let Ok(params) = serde_json::from_value::<DidChangeConfigurationParams>(not.params)
            else {
                return;
            };
            let Some(section) = params.settings.get("jssStyleChecker") else {
                return;
            };
            if !section.is_object() {
                return;
            }
            state.config.client_settings = section.clone();
            let run_on = section.get("runOn").and_then(|v| v.as_str());
            state.config.run_on = if run_on == Some("save") {
                "save".to_string()
            } else {
                "change".to_string()
            };
            relint_open_documents(connection, state);
        }
        "workspace/didChangeWatchedFiles" => {
            let Ok(params) = serde_json::from_value::<DidChangeWatchedFilesParams>(not.params)
            else {
                return;
            };
            for change in params.changes {
                let Some(path) = uri_to_path(change.uri.as_str()) else {
                    continue;
                };
                if path.file_name().and_then(|n| n.to_str()) != Some(".jss-lint.toml") {
                    continue;
                }
                let ok = config_watch::reload(&mut state.config, &path, |m| {
                    let params = ShowMessageParams {
                        typ: MessageType::ERROR,
                        message: m.to_string(),
                    };
                    let _ = connection
                        .sender
                        .send(Message::Notification(Notification::new(
                            ShowMessage::METHOD.to_string(),
                            params,
                        )));
                });
                if !ok {
                    continue;
                }
                relint_open_documents(connection, state);
            }
        }
        _ => {}
    }
}

/// Mirrors `server.py::_code_action`.
fn compute_code_actions(
    state: &ServerState,
    params: &CodeActionParams,
) -> Vec<CodeActionOrCommand> {
    let uri = params.text_document.uri.to_string();
    let Some(entry) = state.cache.get(&uri) else {
        return vec![];
    };
    let Some(doc) = state.docs.get(&uri) else {
        return vec![];
    };
    let req_start = params.range.start.line;
    let req_end = params.range.end.line;

    let mut actions = Vec::new();
    for v in &entry.violations {
        if v.fix.is_none() {
            continue;
        }
        let line = v.line.saturating_sub(1);
        if !(req_start <= line && line <= req_end) {
            continue;
        }
        let Some(ca) = jsslint_core::lsp::violation_to_code_action(v, &doc.text, &uri) else {
            continue;
        };
        let Ok(action_uri) = ca.uri.parse::<Uri>() else {
            continue;
        };
        // lsp_types::Uri wraps fluent_uri, whose internal Cell trips
        // clippy's mutable-key-type lint; Uri's Hash/Eq are pure
        // string comparisons (`self.as_str()`), so it's safe as a key.
        #[allow(clippy::mutable_key_type)]
        let mut changes = HashMap::new();
        changes.insert(action_uri, vec![to_lsp_text_edit(&ca.edit)]);
        actions.push(CodeActionOrCommand::CodeAction(CodeAction {
            title: ca.title,
            kind: Some(CodeActionKind::QUICKFIX),
            edit: Some(WorkspaceEdit {
                changes: Some(changes),
                ..Default::default()
            }),
            ..Default::default()
        }));
    }
    actions
}

/// Workspace command `jss-lint.applyAllFixes`: aggregates every
/// safe-confidence fix across open documents into one
/// `workspace/applyEdit` request sent to the client. Mirrors
/// `server.py::_apply_all_fixes`. The client's later response
/// (accepted/rejected) isn't correlated back to a log line — see this
/// module's doc comment.
fn apply_all_fixes(connection: &Connection, state: &mut ServerState) -> serde_json::Value {
    #[allow(clippy::mutable_key_type)]
    let mut changes: HashMap<Uri, Vec<TextEdit>> = HashMap::new();
    for uri in state.cache.open_uris() {
        let Some(doc) = state.docs.get(&uri) else {
            continue;
        };
        let (text, version) = (doc.text.clone(), doc.version);
        if !state.cache.is_current(&uri, version) {
            lint_uri(connection, state, &uri, version, &text);
        }
        let Some(entry) = state.cache.get(&uri) else {
            continue;
        };
        let mut edits: Vec<TextEdit> = entry
            .violations
            .iter()
            .filter_map(|v| {
                let fix = v.fix.as_ref()?;
                if fix.confidence != FixConfidence::Safe {
                    return None;
                }
                Some(to_lsp_text_edit(&jsslint_core::lsp::fix_to_text_edit(
                    fix, &text,
                )))
            })
            .collect();
        if edits.is_empty() {
            continue;
        }
        // Reverse-position order (spec 008): later offsets first so
        // earlier offsets stay valid when the client applies them.
        edits.sort_by(|a, b| {
            (b.range.start.line, b.range.start.character)
                .cmp(&(a.range.start.line, a.range.start.character))
        });
        if let Ok(lsp_uri) = uri.parse::<Uri>() {
            changes.insert(lsp_uri, edits);
        }
    }

    if changes.is_empty() {
        return serde_json::Value::Null;
    }
    let files = changes.len();
    let edits_count: usize = changes.values().map(|v| v.len()).sum();

    let params = ApplyWorkspaceEditParams {
        label: Some("jss-lint: Apply all fixes".to_string()),
        edit: WorkspaceEdit {
            changes: Some(changes),
            ..Default::default()
        },
    };
    state.next_request_id += 1;
    let req = Request::new(
        RequestId::from(state.next_request_id),
        ApplyWorkspaceEdit::METHOD.to_string(),
        params,
    );
    let _ = connection.sender.send(Message::Request(req));

    serde_json::json!({"files": files, "edits": edits_count})
}

fn handle_request(connection: &Connection, state: &mut ServerState, req: Request) {
    match req.method.as_str() {
        "textDocument/codeAction" => {
            let params: CodeActionParams = match serde_json::from_value(req.params) {
                Ok(p) => p,
                Err(_) => {
                    let _ = connection.sender.send(Message::Response(Response::new_err(
                        req.id,
                        ErrorCode::InvalidParams as i32,
                        "invalid codeAction params".to_string(),
                    )));
                    return;
                }
            };
            let actions = compute_code_actions(state, &params);
            let result = serde_json::to_value(actions).unwrap_or(serde_json::Value::Null);
            let _ = connection
                .sender
                .send(Message::Response(Response::new_ok(req.id, result)));
        }
        "workspace/executeCommand" => {
            let params: ExecuteCommandParams = match serde_json::from_value(req.params) {
                Ok(p) => p,
                Err(_) => {
                    let _ = connection.sender.send(Message::Response(Response::new_err(
                        req.id,
                        ErrorCode::InvalidParams as i32,
                        "invalid executeCommand params".to_string(),
                    )));
                    return;
                }
            };
            if params.command == "jss-lint.applyAllFixes" {
                let result = apply_all_fixes(connection, state);
                let _ = connection
                    .sender
                    .send(Message::Response(Response::new_ok(req.id, result)));
            } else {
                let _ = connection.sender.send(Message::Response(Response::new_err(
                    req.id,
                    ErrorCode::MethodNotFound as i32,
                    format!("unknown command: {}", params.command),
                )));
            }
        }
        other => {
            let _ = connection.sender.send(Message::Response(Response::new_err(
                req.id,
                ErrorCode::MethodNotFound as i32,
                format!("unhandled method: {other}"),
            )));
        }
    }
}

fn run_main_loop(connection: &Connection) {
    let mut state = ServerState::new();
    let (debounce_tx, debounce_rx): (Sender<DebounceMsg>, Receiver<DebounceMsg>) = unbounded();

    loop {
        crossbeam_channel::select! {
            recv(connection.receiver) -> msg => {
                let Ok(msg) = msg else { return };
                match msg {
                    Message::Request(req) => {
                        match connection.handle_shutdown(&req) {
                            Ok(true) => return,
                            Ok(false) => handle_request(connection, &mut state, req),
                            Err(_) => return,
                        }
                    }
                    Message::Notification(not) => {
                        if not.method == "exit" {
                            return;
                        }
                        handle_notification(connection, &mut state, &debounce_tx, not);
                    }
                    Message::Response(_) => {
                        // Response to our own outgoing workspace/applyEdit
                        // request — no observable protocol behavior
                        // depends on it (see module doc comment).
                    }
                }
            }
            recv(debounce_rx) -> due => {
                let Ok((uri, gen)) = due else { continue };
                if state.generations.get(&uri) != Some(&gen) {
                    continue;
                }
                if let Some(doc) = state.docs.get(&uri) {
                    let (text, version) = (doc.text.clone(), doc.version);
                    lint_uri(connection, &mut state, &uri, version, &text);
                }
            }
        }
    }
}
