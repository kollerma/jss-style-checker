//! Whether to colourise the terminal stream — mirrors
//! `src/texlint/color.py` (spec 027 item F).
//!
//! Contract: `specs/027-first-time-user-gaps/contracts/color.md`.
//!
//! The *decision* is shared with the Python engine, byte for byte:
//! a user who exports `NO_COLOR` must get the same answer from
//! `jss-lint` and `jsslint` (`color_parity.rs` checks exactly that).
//! The *escape bytes* are not shared — Python lets rich emit them, this
//! engine writes SGR at render time — and that divergence is recorded in
//! `rust/README.md` (§XIII). What both guarantee is C-1: stripping the
//! escapes yields the plain stream byte for byte.

/// The 16-colour SGR set this engine uses (`color.md` C-2). No
/// 256-colour or truecolor sequences: they are unreadable on some
/// backgrounds and unsupported on others.
pub const RESET: &str = "\x1b[0m";
pub const BOLD: &str = "\x1b[1m";
pub const DIM: &str = "\x1b[2m";
pub const RED: &str = "\x1b[31m";
pub const YELLOW: &str = "\x1b[33m";
pub const GREEN: &str = "\x1b[32m";
pub const CYAN: &str = "\x1b[36m";

/// Resolve the colour decision. `flag` is `--color`'s value or `None`;
/// `toml_value` is `ToolConfig.color`; `env` looks up an environment
/// variable; `isatty` is whether stdout is a terminal.
///
/// Precedence, as anstream/ripgrep/cargo have it:
/// `--color` > `NO_COLOR` > `CLICOLOR_FORCE` > TOML > TTY.
pub fn should_colorize(
    flag: Option<&str>,
    toml_value: ColorChoice,
    env: &dyn Fn(&str) -> Option<String>,
    isatty: bool,
) -> bool {
    match flag {
        Some("always") => return true,
        Some("never") => return false,
        _ => {}
    }

    // `NO_COLOR` is honoured when set to anything non-empty; an empty
    // value is how a script neutralises an inherited one.
    if env("NO_COLOR").is_some_and(|v| !v.is_empty()) {
        return false;
    }
    // `CLICOLOR_FORCE` forces colour on, except the documented `0`.
    if env("CLICOLOR_FORCE").is_some_and(|v| !v.is_empty() && v != "0") {
        return true;
    }

    match toml_value {
        ColorChoice::Always => true,
        ColorChoice::Never => false,
        ColorChoice::Auto => {
            isatty && env("TERM").unwrap_or_default() != "dumb"
        }
    }
}

/// Colour policy recorded in `.jss-lint.toml` — intent, not decision.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum ColorChoice {
    #[default]
    Auto,
    Always,
    Never,
}

impl ColorChoice {
    pub fn parse(value: &str) -> Option<Self> {
        match value {
            "auto" => Some(Self::Auto),
            "always" => Some(Self::Always),
            "never" => Some(Self::Never),
            _ => None,
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Auto => "auto",
            Self::Always => "always",
            Self::Never => "never",
        }
    }
}

/// Wrap `text` in `style` when colour is on. Widths are always measured
/// on the unstyled text, so a styled cell occupies exactly as many
/// columns as a plain one (`color.md` C-1).
pub fn paint(text: &str, style: &str, color: bool) -> String {
    if color && !text.is_empty() {
        format!("{style}{text}{RESET}")
    } else {
        text.to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn env_of<'a>(pairs: &'a [(&'a str, &'a str)]) -> impl Fn(&str) -> Option<String> + 'a {
        move |key| {
            pairs
                .iter()
                .find(|(k, _)| *k == key)
                .map(|(_, v)| v.to_string())
        }
    }

    fn decide(flag: Option<&str>, toml: ColorChoice, pairs: &[(&str, &str)], isatty: bool) -> bool {
        should_colorize(flag, toml, &env_of(pairs), isatty)
    }

    #[test]
    fn flag_beats_everything() {
        assert!(decide(Some("always"), ColorChoice::Never, &[("NO_COLOR", "1")], false));
        assert!(!decide(Some("never"), ColorChoice::Always, &[("CLICOLOR_FORCE", "1")], true));
    }

    #[test]
    fn no_color_beats_clicolor_force() {
        assert!(!decide(None, ColorChoice::Auto, &[("NO_COLOR", "1"), ("CLICOLOR_FORCE", "1")], true));
    }

    #[test]
    fn empty_values_are_ignored() {
        assert!(decide(None, ColorChoice::Auto, &[("NO_COLOR", "")], true));
        assert!(!decide(None, ColorChoice::Auto, &[("CLICOLOR_FORCE", "")], false));
        assert!(!decide(None, ColorChoice::Auto, &[("CLICOLOR_FORCE", "0")], false));
    }

    #[test]
    fn toml_then_tty() {
        assert!(decide(None, ColorChoice::Always, &[], false));
        assert!(!decide(None, ColorChoice::Never, &[], true));
        assert!(decide(None, ColorChoice::Auto, &[], true));
        assert!(!decide(None, ColorChoice::Auto, &[], false));
    }

    #[test]
    fn a_dumb_terminal_is_not_coloured() {
        assert!(!decide(None, ColorChoice::Auto, &[("TERM", "dumb")], true));
        assert!(decide(Some("always"), ColorChoice::Auto, &[("TERM", "dumb")], true));
    }

    #[test]
    fn paint_is_a_no_op_without_colour() {
        assert_eq!(paint("warning", YELLOW, false), "warning");
        assert_eq!(paint("warning", YELLOW, true), "\x1b[33mwarning\x1b[0m");
        // An empty cell stays empty: wrapping it would add bytes that
        // strip to nothing but widen no column.
        assert_eq!(paint("", YELLOW, true), "");
    }
}
