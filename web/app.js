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
import { decompressionSupported, readZip } from "./zip.js";

const SUPPORTED_SUFFIXES = [".tex", ".ltx", ".bib", ".rnw", ".rmd"];

/** True for a path worth handing the engine (spec 027 item E).
 *
 * Overleaf's source zip carries the whole project — figures, PDFs,
 * sometimes a macOS resource fork per file. Only the sources are
 * lintable, and `__MACOSX/`/`._*` entries would otherwise arrive as
 * mojibake "files" with the same names as the real ones.
 */
function isLintablePath(path) {
  const lower = path.toLowerCase();
  if (lower.startsWith("__macosx/") || lower.includes("/__macosx/")) return false;
  if (path.split("/").pop().startsWith("._")) return false;
  return SUPPORTED_SUFFIXES.some((suffix) => lower.endsWith(suffix));
}

const zipButton = document.getElementById("zip-button");
const zipInput = document.getElementById("zip-input");
const dropZone = document.getElementById("drop-zone");
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
  zipButton.disabled = disabled;
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
    isLintablePath(f.webkitRelativePath || f.name)
  );

  resultsFrame.style.display = "none";
  resultsFrame.srcdoc = "";
  lastPairs = null;

  if (files.length === 0) {
    setStatus(
      `No .tex/.ltx/.bib/.Rnw/.Rmd files found among the ${allFiles.length} file(s) selected.`,
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

/** Check one Overleaf-style source zip, unpacked in this tab. */
async function handleZip(file) {
  resultsFrame.style.display = "none";
  resultsFrame.srcdoc = "";
  lastPairs = null;

  if (!decompressionSupported()) {
    setStatus(
      "This browser cannot unpack zip files (no DecompressionStream). " +
        "Unzip the download and use \u201cChoose a folder\u2026\u201d instead.",
      true
    );
    return;
  }

  setPickersDisabled(true);
  try {
    setStatus(`Unpacking ${file.name}\u2026`);
    const pairs = await readZip(await file.arrayBuffer(), isLintablePath);
    if (pairs.length === 0) {
      setStatus(
        `No .tex/.ltx/.bib/.Rnw/.Rmd files inside ${file.name}.`,
        true
      );
      return;
    }
    // Entry paths are kept as the keys, so multi-file resolution and
    // the report's file headings match the project's own layout.
    lastPairs = pairs;

    await ready;
    setStatus(`Checking ${pairs.length} file(s)\u2026`);
    renderReport();
    setStatus(`Checked ${pairs.length} file(s) from ${file.name}.`);
  } catch (err) {
    lastPairs = null;
    setStatus(`Could not read ${file.name}: ${err.message || err}`, true);
  } finally {
    setPickersDisabled(false);
    zipInput.value = "";
  }
}

zipButton.addEventListener("click", () => zipInput.click());
zipInput.addEventListener("change", () => {
  const file = zipInput.files[0];
  if (file) handleZip(file);
});

// Drag-and-drop: a zip anywhere on the panel, which is what a user does
// with a freshly downloaded Overleaf export.
["dragenter", "dragover"].forEach((name) =>
  dropZone.addEventListener(name, (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
  })
);
["dragleave", "drop"].forEach((name) =>
  dropZone.addEventListener(name, (event) => {
    event.preventDefault();
    if (name === "dragleave" && dropZone.contains(event.relatedTarget)) return;
    dropZone.classList.remove("dragging");
  })
);
dropZone.addEventListener("drop", (event) => {
  const items = Array.from(event.dataTransfer.files);
  const zip = items.find((f) => f.name.toLowerCase().endsWith(".zip"));
  if (zip) {
    handleZip(zip);
    return;
  }
  const lintable = items.filter((f) => isLintablePath(f.name));
  if (lintable.length > 0) {
    handlePickedFiles(filesInput, lintable);
    return;
  }
  setStatus(
    "Drop a .zip from Overleaf (Menu \u2192 Download \u2192 Source), or " +
      ".tex/.bib files.",
    true
  );
});

folderInput.addEventListener("change", () =>
  handlePickedFiles(folderInput, Array.from(folderInput.files))
);
filesInput.addEventListener("change", () =>
  handlePickedFiles(filesInput, Array.from(filesInput.files))
);
