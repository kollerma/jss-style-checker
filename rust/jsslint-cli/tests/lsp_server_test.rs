//! End-to-end acceptance test for `jsslint lsp`: this is a stateful
//! bidirectional protocol, not a batch CLI command, so it can't be
//! differentially tested by diffing stdout against the Python binary
//! the way every other subcommand in this port is (see
//! `jsslint_cli::lsp_server`'s module doc comment). Instead this test
//! acts as a real LSP client — speaking the actual Content-Length-
//! framed JSON-RPC wire format over the compiled binary's real
//! stdin/stdout via `lsp_server::Message` — and asserts on published
//! diagnostics and code actions for a real auto-fix fixture with a
//! known violation. The projection logic producing those diagnostics/
//! actions (`jsslint_core::lsp`) is separately differentially
//! validated against `texlint.lsp.conversions` in
//! `jsslint-core/tests/lsp_parity.rs` — this test's job is the
//! protocol plumbing (message framing, document tracking, dispatch),
//! not re-proving that projection logic.

use lsp_server::{Message, Notification, Request, RequestId, Response};
use lsp_types::{
    CodeActionContext, CodeActionParams, DidOpenTextDocumentParams, PartialResultParams, Position,
    PublishDiagnosticsParams, Range, TextDocumentIdentifier, TextDocumentItem,
    WorkDoneProgressParams,
};
use serde_json::json;
use std::io::{BufReader, Write};
use std::path::PathBuf;
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::time::Duration;

/// Asserts a response is `Ok` and returns its result payload, panicking
/// with the full response (including the error) otherwise. lsp-server 0.10
/// models `Response::response_result` as `Result<Value, ResponseError>`
/// rather than separate `result`/`error` fields, so "no error" and "has a
/// result" are the same fact — this asserts both at once.
fn expect_ok_result(resp: &Response, action: &str) -> serde_json::Value {
    match &resp.response_result {
        Ok(value) => value.clone(),
        Err(err) => panic!("{action} returned an error: {resp:?} ({err:?})"),
    }
}

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf()
}

struct Client {
    child: Child,
    stdin: ChildStdin,
    stdout: BufReader<ChildStdout>,
    next_id: i32,
}

impl Client {
    fn spawn() -> Self {
        let mut child = Command::new(env!("CARGO_BIN_EXE_jsslint"))
            .arg("lsp")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .expect("failed to spawn jsslint lsp");
        let stdin = child.stdin.take().unwrap();
        let stdout = BufReader::new(child.stdout.take().unwrap());
        Self {
            child,
            stdin,
            stdout,
            next_id: 1,
        }
    }

    fn send(&mut self, msg: Message) {
        msg.write(&mut self.stdin).expect("failed to write message");
        self.stdin.flush().expect("failed to flush stdin");
    }

    fn recv(&mut self) -> Message {
        Message::read(&mut self.stdout)
            .expect("failed to read message")
            .expect("connection closed unexpectedly")
    }

    fn request(&mut self, method: &str, params: impl serde::Serialize) -> RequestId {
        let id = RequestId::from(self.next_id);
        self.next_id += 1;
        self.send(Message::Request(Request::new(
            id.clone(),
            method.to_string(),
            params,
        )));
        id
    }

    fn notify(&mut self, method: &str, params: impl serde::Serialize) {
        self.send(Message::Notification(Notification::new(
            method.to_string(),
            params,
        )));
    }

    /// Reads messages until a `Response` with the given id arrives,
    /// collecting any notifications seen along the way.
    fn expect_response(&mut self, id: &RequestId) -> (Response, Vec<Notification>) {
        let mut notifications = Vec::new();
        loop {
            match self.recv() {
                Message::Response(r) if &r.id == id => return (r, notifications),
                Message::Notification(n) => notifications.push(n),
                other => panic!("unexpected message while waiting for response {id:?}: {other:?}"),
            }
        }
    }

    fn expect_notification(&mut self, method: &str) -> Notification {
        loop {
            match self.recv() {
                Message::Notification(n) if n.method == method => return n,
                Message::Notification(_) => continue,
                other => panic!("unexpected message while waiting for {method}: {other:?}"),
            }
        }
    }

    /// Like `expect_response`, but also auto-answers any server-issued
    /// `workspace/applyEdit` request it sees along the way (as a real
    /// editor would) with `{"applied": true}`, returning it separately.
    fn expect_response_answering_apply_edit(
        &mut self,
        id: &RequestId,
    ) -> (Response, Option<Request>) {
        loop {
            match self.recv() {
                Message::Response(r) if &r.id == id => return (r, None),
                Message::Request(req) if req.method == "workspace/applyEdit" => {
                    self.send(Message::Response(Response::new_ok(
                        req.id.clone(),
                        json!({"applied": true}),
                    )));
                    return (self.expect_response(id).0, Some(req));
                }
                Message::Notification(_) => continue,
                other => panic!("unexpected message while waiting for response {id:?}: {other:?}"),
            }
        }
    }

    fn shutdown_and_exit(&mut self) {
        let id = self.request("shutdown", json!(null));
        let (resp, _) = self.expect_response(&id);
        expect_ok_result(&resp, "shutdown");
        self.notify("exit", json!(null));
        let status = self
            .child
            .wait_timeout(Duration::from_secs(5))
            .expect("failed to wait on child")
            .expect("jsslint lsp did not exit after `exit` notification");
        assert!(status.success(), "jsslint lsp exited non-zero: {status:?}");
    }
}

// `std::process::Child` has no built-in `wait_timeout`; a tiny local
// extension avoids pulling in the `wait-timeout` crate for one test.
trait WaitTimeoutExt {
    fn wait_timeout(
        &mut self,
        timeout: Duration,
    ) -> std::io::Result<Option<std::process::ExitStatus>>;
}

impl WaitTimeoutExt for Child {
    fn wait_timeout(
        &mut self,
        timeout: Duration,
    ) -> std::io::Result<Option<std::process::ExitStatus>> {
        let deadline = std::time::Instant::now() + timeout;
        loop {
            if let Some(status) = self.try_wait()? {
                return Ok(Some(status));
            }
            if std::time::Instant::now() >= deadline {
                return Ok(None);
            }
            std::thread::sleep(Duration::from_millis(20));
        }
    }
}

fn initialize(client: &mut Client) {
    let id = client.request(
        "initialize",
        json!({"processId": null, "rootUri": null, "capabilities": {}}),
    );
    let (resp, _) = client.expect_response(&id);
    let result = expect_ok_result(&resp, "initialize");
    assert_eq!(
        result["capabilities"]["codeActionProvider"], true,
        "server must advertise code action support"
    );
    client.notify("initialized", json!({}));
}

#[test]
fn lsp_publishes_diagnostics_and_code_action_for_a_known_violation() {
    let root = repo_root();
    let fixture = root.join("tests/fixtures/auto-fix/JSS-MARKUP-001/before.tex");
    let text = std::fs::read_to_string(&fixture).expect("failed to read fixture");
    let uri: lsp_types::Uri = "file:///tmp/lsp-test/before.tex".parse().unwrap();

    let mut client = Client::spawn();
    initialize(&mut client);

    client.notify(
        "textDocument/didOpen",
        DidOpenTextDocumentParams {
            text_document: TextDocumentItem {
                uri: uri.clone(),
                language_id: "latex".to_string(),
                version: 1,
                text: text.clone(),
            },
        },
    );

    let diag_notification = client.expect_notification("textDocument/publishDiagnostics");
    let params: PublishDiagnosticsParams =
        serde_json::from_value(diag_notification.params).expect("valid publishDiagnostics params");
    assert_eq!(params.uri.as_str(), uri.as_str());
    assert!(
        params.diagnostics.iter().any(|d| d.code
            == Some(lsp_types::NumberOrString::String(
                "JSS-MARKUP-001".to_string()
            ))),
        "expected a JSS-MARKUP-001 diagnostic, got: {:?}",
        params.diagnostics
    );
    let markup_diag = params
        .diagnostics
        .iter()
        .find(|d| {
            d.code
                == Some(lsp_types::NumberOrString::String(
                    "JSS-MARKUP-001".to_string(),
                ))
        })
        .unwrap();
    assert_eq!(
        markup_diag.severity,
        Some(lsp_types::DiagnosticSeverity::WARNING)
    );
    assert_eq!(markup_diag.source.as_deref(), Some("jss-lint"));

    // Request code actions over the whole document; expect a quickfix
    // that wraps the offending token in \proglang{}.
    let id = client.request(
        "textDocument/codeAction",
        CodeActionParams {
            text_document: TextDocumentIdentifier { uri: uri.clone() },
            range: Range {
                start: Position {
                    line: 0,
                    character: 0,
                },
                end: Position {
                    line: 200,
                    character: 0,
                },
            },
            context: CodeActionContext {
                diagnostics: vec![],
                only: None,
                trigger_kind: None,
            },
            work_done_progress_params: WorkDoneProgressParams::default(),
            partial_result_params: PartialResultParams::default(),
        },
    );
    let (resp, _) = client.expect_response(&id);
    let result = expect_ok_result(&resp, "codeAction");
    let actions: Vec<lsp_types::CodeActionOrCommand> =
        serde_json::from_value(result).expect("valid CodeActionOrCommand array");
    assert!(!actions.is_empty(), "expected at least one code action");
    let lsp_types::CodeActionOrCommand::CodeAction(action) = &actions[0] else {
        panic!("expected a CodeAction, got a Command");
    };
    assert_eq!(action.kind, Some(lsp_types::CodeActionKind::QUICKFIX));
    let edit = action
        .edit
        .as_ref()
        .expect("code action must carry a WorkspaceEdit");
    #[allow(clippy::mutable_key_type)] // see mod.rs's comment at the same lint
    let changes = edit.changes.as_ref().expect("edit must have changes");
    let edits = changes.get(&uri).expect("edit must target the opened uri");
    assert_eq!(edits.len(), 1);
    assert!(
        edits[0].new_text.contains("\\proglang{Python}"),
        "expected the fix to wrap Python in \\proglang{{}}, got: {:?}",
        edits[0].new_text
    );

    // didClose must clear diagnostics (publish an empty array).
    client.notify(
        "textDocument/didClose",
        lsp_types::DidCloseTextDocumentParams {
            text_document: TextDocumentIdentifier { uri: uri.clone() },
        },
    );
    let close_notification = client.expect_notification("textDocument/publishDiagnostics");
    let close_params: PublishDiagnosticsParams =
        serde_json::from_value(close_notification.params).unwrap();
    assert_eq!(close_params.uri.as_str(), uri.as_str());
    assert!(close_params.diagnostics.is_empty());

    client.shutdown_and_exit();
}

#[test]
fn lsp_suppresses_a_rule_via_did_change_configuration() {
    let root = repo_root();
    let fixture = root.join("tests/fixtures/auto-fix/JSS-MARKUP-001/before.tex");
    let text = std::fs::read_to_string(&fixture).expect("failed to read fixture");
    let uri: lsp_types::Uri = "file:///tmp/lsp-test/config.tex".parse().unwrap();

    let mut client = Client::spawn();
    initialize(&mut client);

    client.notify(
        "textDocument/didOpen",
        DidOpenTextDocumentParams {
            text_document: TextDocumentItem {
                uri: uri.clone(),
                language_id: "latex".to_string(),
                version: 1,
                text: text.clone(),
            },
        },
    );
    let opened = client.expect_notification("textDocument/publishDiagnostics");
    let opened_params: PublishDiagnosticsParams = serde_json::from_value(opened.params).unwrap();
    assert!(
        opened_params.diagnostics.iter().any(|d| d.code
            == Some(lsp_types::NumberOrString::String(
                "JSS-MARKUP-001".to_string()
            ))),
        "fixture must produce JSS-MARKUP-001 before any client settings are pushed"
    );

    // Push jssStyleChecker.ignoreRules = ["JSS-MARKUP-001"]; the server
    // must re-lint every open document and the rule must disappear.
    client.notify(
        "workspace/didChangeConfiguration",
        lsp_types::DidChangeConfigurationParams {
            settings: json!({"jssStyleChecker": {"ignoreRules": ["JSS-MARKUP-001"]}}),
        },
    );
    let relint = client.expect_notification("textDocument/publishDiagnostics");
    let relint_params: PublishDiagnosticsParams = serde_json::from_value(relint.params).unwrap();
    assert!(
        !relint_params
            .diagnostics
            .iter()
            .any(|d| d.code == Some(lsp_types::NumberOrString::String("JSS-MARKUP-001".to_string()))),
        "JSS-MARKUP-001 must be suppressed after ignoreRules is pushed via client settings, got: {:?}",
        relint_params.diagnostics
    );

    client.shutdown_and_exit();
}

#[test]
fn lsp_debounces_did_change_and_applies_all_fixes_via_execute_command() {
    let root = repo_root();
    let fixture = root.join("tests/fixtures/auto-fix/JSS-MARKUP-001/before.tex");
    let before_text = std::fs::read_to_string(&fixture).expect("failed to read fixture");
    let uri: lsp_types::Uri = "file:///tmp/lsp-test/debounce.tex".parse().unwrap();

    let mut client = Client::spawn();
    initialize(&mut client);

    client.notify(
        "textDocument/didOpen",
        DidOpenTextDocumentParams {
            text_document: TextDocumentItem {
                uri: uri.clone(),
                language_id: "latex".to_string(),
                version: 1,
                text: before_text.clone(),
            },
        },
    );
    // Drain the immediate didOpen diagnostics before exercising didChange.
    client.expect_notification("textDocument/publishDiagnostics");

    // A didChange with the SAME violation-carrying content: the server
    // must debounce (~200ms) rather than lint synchronously. Confirm
    // no diagnostics notification shows up immediately, then confirm
    // one does arrive within a generous window — proving the debounce
    // timer actually fires, not just that debouncing "doesn't crash".
    client.notify(
        "textDocument/didChange",
        lsp_types::DidChangeTextDocumentParams {
            text_document: lsp_types::VersionedTextDocumentIdentifier {
                uri: uri.clone(),
                version: 2,
            },
            content_changes: vec![lsp_types::TextDocumentContentChangeEvent {
                range: None,
                range_length: None,
                text: before_text.clone(),
            }],
        },
    );
    let start = std::time::Instant::now();
    let notification = client.expect_notification("textDocument/publishDiagnostics");
    let elapsed = start.elapsed();
    assert!(
        elapsed >= Duration::from_millis(150),
        "expected the didChange lint to be debounced (~200ms), but it arrived after {elapsed:?}"
    );
    assert!(
        elapsed < Duration::from_secs(5),
        "debounced lint took implausibly long: {elapsed:?}"
    );
    let params: PublishDiagnosticsParams = serde_json::from_value(notification.params).unwrap();
    assert!(params.diagnostics.iter().any(|d| d.code
        == Some(lsp_types::NumberOrString::String(
            "JSS-MARKUP-001".to_string()
        ))));

    // jss-lint.applyAllFixes: expect the server to issue a
    // workspace/applyEdit request (auto-answered above) and the
    // executeCommand response to summarize one file / one edit.
    let id = client.request(
        "workspace/executeCommand",
        lsp_types::ExecuteCommandParams {
            command: "jss-lint.applyAllFixes".to_string(),
            arguments: vec![],
            work_done_progress_params: WorkDoneProgressParams::default(),
        },
    );
    let (resp, apply_edit_req) = client.expect_response_answering_apply_edit(&id);
    let summary = expect_ok_result(&resp, "executeCommand");
    let apply_edit_req = apply_edit_req.expect("server must issue a workspace/applyEdit request");
    let edit_params: lsp_types::ApplyWorkspaceEditParams =
        serde_json::from_value(apply_edit_req.params).unwrap();
    #[allow(clippy::mutable_key_type)] // see mod.rs's comment at the same lint
    let changes = edit_params
        .edit
        .changes
        .expect("applyEdit must carry changes");
    let edits = changes
        .get(&uri)
        .expect("applyEdit must target the open document");
    assert_eq!(
        edits.len(),
        1,
        "expected exactly one safe fix to be aggregated"
    );
    assert!(edits[0].new_text.contains("\\proglang{Python}"));

    assert_eq!(summary["files"], 1);
    assert_eq!(summary["edits"], 1);

    client.shutdown_and_exit();
}
