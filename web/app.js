// Minimal browser front-end for the jsslint-wasm binding (spec 018).
// Loads the WASM engine, lets the user pick local files — either a whole
// folder via the native directory picker, or an individual multi-select for
// folders too large/messy to hand the browser wholesale — filters them down
// to the file types the engine understands, and renders the check via the
// same `--output html` renderer the CLI's `--output html` flag uses
// (jsslint_core::html_output — a full standalone HTML document), injected
// into a sandboxed iframe. No network request happens after the initial
// page/wasm load: this is the point of the WASM build.

import init, { render } from "./pkg/jsslint_wasm.js";

const SUPPORTED_SUFFIXES = [".tex", ".ltx", ".bib"];

const folderButton = document.getElementById("folder-button");
const folderInput = document.getElementById("folder-input");
const filesButton = document.getElementById("files-button");
const filesInput = document.getElementById("files-input");
const modeSelect = document.getElementById("mode-select");
const statusEl = document.getElementById("status");
const resultsFrame = document.getElementById("results");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function setPickersDisabled(disabled) {
  folderButton.disabled = disabled;
  filesButton.disabled = disabled;
}

const ready = init()
  .then(() => {
    setStatus("Ready — choose a folder or select files to check.");
    setPickersDisabled(false);
  })
  .catch((err) => {
    setStatus(`Failed to load the checker engine: ${err}`, true);
  });

setPickersDisabled(true);
folderButton.addEventListener("click", () => folderInput.click());
filesButton.addEventListener("click", () => filesInput.click());

// Cached [relativePath, content] pairs from the last successful read, so
// switching Author/Reviewer mode re-renders instantly instead of doing
// nothing until the next file pick.
let lastPairs = null;

function renderReport() {
  if (!lastPairs) return;
  const html = render({
    files: lastPairs,
    output: "html",
    mode: modeSelect.value,
  });
  resultsFrame.srcdoc = html;
  resultsFrame.style.display = "block";
}

modeSelect.addEventListener("change", () => {
  if (!lastPairs) return;
  renderReport();
  setStatus(`Checked ${lastPairs.length} file(s) — ${modeSelect.value} mode.`);
});

async function handlePickedFiles(input, allFiles) {
  const files = allFiles.filter((f) =>
    SUPPORTED_SUFFIXES.some((suffix) => f.name.toLowerCase().endsWith(suffix))
  );

  resultsFrame.style.display = "none";
  resultsFrame.srcdoc = "";
  lastPairs = null;

  if (files.length === 0) {
    setStatus(
      `No .tex/.ltx/.bib files found among the ${allFiles.length} file(s) selected.`,
      true
    );
    // Reset so re-selecting the same folder/files (e.g. after adding a
    // .tex file) reliably fires `change` again — most browsers won't
    // re-fire it for an unchanged selection otherwise.
    input.value = "";
    return;
  }

  setPickersDisabled(true);
  try {
    setStatus(`Reading ${files.length} file(s)…`);
    lastPairs = await Promise.all(
      files.map(async (f) => [f.webkitRelativePath || f.name, await f.text()])
    );

    await ready;
    setStatus(`Checking ${files.length} file(s)…`);
    renderReport();
    setStatus(`Checked ${files.length} file(s).`);
  } catch (err) {
    lastPairs = null;
    setStatus(`Error: ${err}`, true);
  } finally {
    setPickersDisabled(false);
    // Allow re-selecting the same folder/files to re-check after edits.
    input.value = "";
  }
}

folderInput.addEventListener("change", () =>
  handlePickedFiles(folderInput, Array.from(folderInput.files))
);
filesInput.addEventListener("change", () =>
  handlePickedFiles(filesInput, Array.from(filesInput.files))
);
