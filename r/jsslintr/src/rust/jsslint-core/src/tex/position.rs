//! `pos_to_lineno_colno` port — mirrors `pylatexenc.latexwalker`'s
//! method of the same name (empirically verified: 1-based line, 0-based
//! column, both counted in codepoints, splitting on `\n`).
//!
//! `_helpers.py::_lineno_col` then adds 1 to the column to get the
//! 1-based column `Violation` actually carries — that final `+1` step
//! belongs to the rule layer (Phase 3), not here; this module only
//! reproduces the walker-level primitive.

/// Precomputed newline codepoint-offsets for O(log n) line lookup —
/// same idea as `pylatexenc`'s internal line-boundary cache.
pub struct LineIndex {
    /// Offset of each `\n` character in the source.
    newline_positions: Vec<usize>,
    /// Added to every `lineno_colno` line result. Zero for a normal
    /// `.tex`/`.rnw` file; non-zero for a `.Rmd` raw-LaTeX prose
    /// fragment, whose `chars`/`nodes` positions stay fragment-local
    /// (matching Python's `node.pos`, which `_OffsetWalker` never
    /// touches) while reported line numbers must still be
    /// source-accurate on the original `.Rmd`. Mirrors
    /// `rmd_parser.py::_OffsetWalker.pos_to_lineno_colno`'s `line +
    /// self._offset`, applied here instead of via a wrapper type.
    line_offset: u32,
}

impl LineIndex {
    pub fn new(chars: &[char]) -> Self {
        Self::with_offset(chars, 0)
    }

    /// Like [`Self::new`], but every `lineno_colno` result has
    /// `offset` added to its line. `pos` arguments stay relative to
    /// `chars` as given (fragment-local), not to the offset target.
    pub fn with_offset(chars: &[char], offset: u32) -> Self {
        let newline_positions = chars
            .iter()
            .enumerate()
            .filter(|(_, &c)| c == '\n')
            .map(|(i, _)| i)
            .collect();
        Self {
            newline_positions,
            line_offset: offset,
        }
    }

    /// Returns `(1-based line, 0-based column)`, both in codepoints.
    pub fn lineno_colno(&self, pos: usize) -> (u32, u32) {
        // Number of newlines strictly before `pos` = 0-based line index.
        let line_idx = self.newline_positions.partition_point(|&nl| nl < pos);
        let line = (line_idx + 1) as u32 + self.line_offset;
        let line_start = if line_idx == 0 {
            0
        } else {
            self.newline_positions[line_idx - 1] + 1
        };
        let col = (pos - line_start) as u32;
        (line, col)
    }
}
