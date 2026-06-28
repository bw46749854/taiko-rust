//! Optional visual-state projection support for the OpenTaiko Phase1 autonomous loop.
//!
//! This crate currently exposes the minimal Phase1 evidence surface used by smoke
//! tests. Full gameplay rendering behavior is tracked by the Phase1 feature
//! tickets and the Phase1 normal-play compatibility contract.

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
