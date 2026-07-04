# Debugging the extension

1. Open this folder (`vscode-extension/`) in VS Code.
2. Press **F5** — this runs the `npm: watch` build task, then launches a
   second VS Code window (the **Extension Development Host**) with the
   extension loaded.
3. Set breakpoints in `src/extension.ts`; source maps are enabled, so they
   bind to the TypeScript.
4. After code changes, the watcher recompiles automatically — reload the
   Extension Host window with **Ctrl+R** (or "Developer: Reload Window") to
   pick them up.

## Notes

- Pick **"Run Extension"** if F5 ever shows a debugger-type menu. **Do not**
  pick "Node.js": it runs `node ./out/extension.js` directly, which fails
  with `Cannot find module 'vscode'` because the `vscode` API only exists
  inside the Extension Host runtime.
- Config lives in `.vscode/launch.json` (`type: extensionHost`) and
  `.vscode/tasks.json` (`npm: watch`).

## Dogfooding on the recall corpus

To try the extension against the corpus papers, open the multi-root
workspace at the repo root:

```
code recall-corpus.code-workspace
```

It surfaces the repo root plus each corpus paper as a top-level folder.
Launch the Extension Development Host with **F5** from a window opened on
this `vscode-extension/` folder (step 2 above); the host picks up the
`recall-corpus.code-workspace` folders and the LSP wires up automatically.

