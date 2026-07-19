/* tslint:disable */
/* eslint-disable */

/**
 * Lints `request.files` and returns the violations as structured data
 * (camelCase), each carrying its auto-fix (`fix`) when one exists. Unlike
 * `render(output:"json")` — whose `fix` field is hardcoded null for
 * byte-parity with the Python contract — this exposes the real fixes so a
 * UI (e.g. the VS Code extension) can offer per-diagnostic quick fixes.
 */
export function analyze(request: any): any;

/**
 * Applies every available auto-fix in memory and returns the files whose
 * contents changed, as `[path, fixedContents]` pairs (same shape as the
 * `files` input). Files with no applicable fix are omitted. Takes the same
 * request shape as `render`; the `output` field is ignored. No filesystem
 * access — the caller writes the results back however it likes.
 */
export function fix(request: any): any;

/**
 * Lints `request.files` and renders the report in `request.output`
 * format. Mirrors `jsslint::render` / `jsslint-cli`'s bare-lint
 * invocation. `request` is a JS object shaped like `LintRequest`
 * (camelCase keys: `files`, `journal`, `mode`, `output`, `ignoreRules`,
 * `minConfidence`, `failOn`, `sourceRoot`, `verbose`, `codeWidth`,
 * `severityOverrides`).
 */
export function render(request: any): string;

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
    readonly memory: WebAssembly.Memory;
    readonly analyze: (a: any) => [number, number, number];
    readonly fix: (a: any) => [number, number, number];
    readonly render: (a: any) => [number, number, number, number];
    readonly __wbindgen_malloc: (a: number, b: number) => number;
    readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
    readonly __wbindgen_exn_store: (a: number) => void;
    readonly __externref_table_alloc: () => number;
    readonly __wbindgen_externrefs: WebAssembly.Table;
    readonly __externref_table_dealloc: (a: number) => void;
    readonly __wbindgen_free: (a: number, b: number, c: number) => void;
    readonly __wbindgen_start: () => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;

/**
 * Instantiates the given `module`, which can either be bytes or
 * a precompiled `WebAssembly.Module`.
 *
 * @param {{ module: SyncInitInput }} module - Passing `SyncInitInput` directly is deprecated.
 *
 * @returns {InitOutput}
 */
export function initSync(module: { module: SyncInitInput } | SyncInitInput): InitOutput;

/**
 * If `module_or_path` is {RequestInfo} or {URL}, makes a request and
 * for everything else, calls `WebAssembly.instantiate` directly.
 *
 * @param {{ module_or_path: InitInput | Promise<InitInput> }} module_or_path - Passing `InitInput` directly is deprecated.
 *
 * @returns {Promise<InitOutput>}
 */
export default function __wbg_init (module_or_path?: { module_or_path: InitInput | Promise<InitInput> } | InitInput | Promise<InitInput>): Promise<InitOutput>;
