// Minimal browser front-end for the jsslint-wasm binding (spec 018).
// Loads the WASM engine, lets the user pick a local folder via the
// native directory picker, filters it down to the file types the
// engine understands, and renders the check via the same
// `--output html` renderer the CLI's `--output html` flag uses
// (jsslint_core::html_output — a full standalone HTML document),
// injected into a sandboxed iframe. No network request happens after
// the initial page/wasm load: this is the point of the WASM build.

import init, { render } from "./pkg/jsslint_wasm.js";

const SUPPORTED_SUFFIXES = [".tex", ".ltx", ".bib"];

const pickButton = document.getElementById("pick-button");
const folderInput = document.getElementById("folder-input");
const modeSelect = document.getElementById("mode-select");
const statusEl = document.getElementById("status");
const resultsFrame = document.getElementById("results");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

const ready = init()
  .then(() => {
    setStatus("Ready — choose a folder to check.");
    pickButton.disabled = false;
  })
  .catch((err) => {
    setStatus(`Failed to load the checker engine: ${err}`, true);
  });

pickButton.disabled = true;
pickButton.addEventListener("click", () => folderInput.click());

folderInput.addEventListener("change", async () => {
  const allFiles = Array.from(folderInput.files);
  const files = allFiles.filter((f) =>
    SUPPORTED_SUFFIXES.some((suffix) => f.name.toLowerCase().endsWith(suffix))
  );

  resultsFrame.style.display = "none";
  resultsFrame.srcdoc = "";

  if (files.length === 0) {
    setStatus(
      `No .tex/.ltx/.bib files found among the ${allFiles.length} file(s) in that folder.`,
      true
    );
    // Reset so re-selecting the same folder (e.g. after adding a .tex
    // file to it) reliably fires `change` again — most browsers won't
    // re-fire it for an unchanged selection otherwise.
    folderInput.value = "";
    return;
  }

  pickButton.disabled = true;
  try {
    setStatus(`Reading ${files.length} file(s)…`);
    const pairs = await Promise.all(
      files.map(async (f) => [f.webkitRelativePath || f.name, await f.text()])
    );

    await ready;
    setStatus(`Checking ${files.length} file(s)…`);

    const html = render({
      files: pairs,
      output: "html",
      mode: modeSelect.value,
    });

    resultsFrame.srcdoc = html;
    resultsFrame.style.display = "block";
    setStatus(`Checked ${files.length} file(s).`);
  } catch (err) {
    setStatus(`Error: ${err}`, true);
  } finally {
    pickButton.disabled = false;
    // Allow re-selecting the same folder to re-check after edits.
    folderInput.value = "";
  }
});
