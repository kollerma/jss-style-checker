//! Dev tool: `cargo run --release --example dump_tex <file.tex>` prints
//! the same debug-dump format as `tools/dump_tex_nodes.py`, for manual
//! or scripted diffing against the Python oracle.

fn main() {
    let path = std::env::args().nth(1).expect("usage: dump_tex <file.tex>");
    let source = std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("read {path}: {e}"));
    let parsed = jsslint_core::tex::parse_tex_source(&source);
    print!("{}", jsslint_core::tex::debug::dump(&parsed.nodes));
}
