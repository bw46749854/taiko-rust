//! Minimal taiko_render skeleton for the OpenTaiko Phase1 autonomous loop.
//!
//! Gameplay implementation is intentionally out of scope for Rust workspace skeleton. This crate
//! exists so later tickets can add Phase1 functionality without renaming the
//! canonical workspace layout.

/// Returns the canonical crate name for workspace and CLI diagnostics.
#[must_use]
pub const fn crate_name() -> &'static str {
    "taiko_render"
}

#[cfg(test)]
mod tests {
    use super::crate_name;

    #[test]
    fn exposes_canonical_crate_name() {
        assert_eq!(crate_name(), "taiko_render");
    }
}
