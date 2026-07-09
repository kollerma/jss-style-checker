//! Core rule engine for the JSS style checker — spec 018 Rust port.
//!
//! This crate contains zero binding-specific code. `jsslint-cli`,
//! `jsslint-wasm`, `jsslint-r`, and `jsslint-py` are thin marshalling
//! layers over the types and functions exported here; see
//! `/home/node/.claude/plans/having-the-style-checker-compressed-crown.md`
//! for the full architecture.

pub mod catalogue;
pub mod json_output;
pub mod report;
pub mod terms;
pub mod tex;

pub use catalogue::{lookup as lookup_rule, RuleMeta};
pub use report::{
    CategoryStatus, CategorySummary, ComplianceReport, Fix, FixConfidence, Severity, SkippedRule,
    Violation,
};
