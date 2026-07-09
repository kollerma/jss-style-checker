//! Debug dump matching `tools/dump_bib_entries.py`'s format exactly —
//! see that script's module doc for the comparison methodology.

use super::model::Library;

fn entry_line(entry: &super::model::Entry) -> String {
    let mut fields: Vec<(String, String)> = entry
        .fields
        .iter()
        .map(|f| (f.key.to_ascii_lowercase(), f.value.trim().to_string()))
        .collect();
    fields.sort();
    let field_str = fields
        .iter()
        .map(|(k, v)| format!("{k}={v}"))
        .collect::<Vec<_>>()
        .join("|");
    format!(
        "ENTRY\t{}\t{}\t{}\t{}",
        entry.key,
        entry.entry_type.to_ascii_lowercase(),
        entry.start_line,
        field_str
    )
}

pub fn dump(library: &Library) -> String {
    let mut lines: Vec<String> = library.entries.iter().map(entry_line).collect();

    let mut dup_keys: Vec<String> = library
        .duplicate_block_keys
        .iter()
        .map(|b| format!("DUPKEY\t{}\t{}", b.key, b.start_line))
        .collect();
    dup_keys.sort();
    lines.extend(dup_keys);

    let mut dup_fields: Vec<String> = library
        .duplicate_field_keys
        .iter()
        .map(|b| format!("DUPFIELD\t{}\t{}", b.start_line, b.duplicate_keys.join(",")))
        .collect();
    dup_fields.sort();
    lines.extend(dup_fields);

    if lines.is_empty() {
        String::new()
    } else {
        lines.join("\n") + "\n"
    }
}
