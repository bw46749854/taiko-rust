//! Timing analyzer MVP for the OpenTaiko Phase1 autonomous loop.
//!
//! Step10 deliberately implements a deterministic analyzer over Step9 headless
//! autoplay evidence. It does not claim OpenTaiko-compatible audio scheduling or
//! judgement-window precision yet. Its purpose is to make timing evidence
//! machine-readable so QA Session can reject parser/runtime regressions and route
//! failures back to repair tickets without manual inspection.

use std::fmt;

/// Returns the canonical crate name for workspace and CLI diagnostics.
#[must_use]
pub const fn crate_name() -> &'static str {
    "taiko_timing"
}

/// Approved timing failure categories for repair-ticket routing.
pub const TIMING_FAILURE_CATEGORIES: &[&str] = &[
    "parser_error",
    "chart_time_error",
    "scroll_time_error",
    "judgement_window_error",
    "autoplay_input_error",
    "runtime_tick_error",
    "headless_autoplay_result_error",
    "timing_cli_contract_error",
];

/// Timing analyzer error.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TimingError {
    InvalidInput(String),
}

impl fmt::Display for TimingError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidInput(message) => write!(f, "invalid timing analyzer input: {message}"),
        }
    }
}

impl std::error::Error for TimingError {}

/// Per-fixture timing analyzer result.
#[derive(Debug, Clone, PartialEq)]
pub struct TimingFixtureResult {
    pub fixture_id: Option<String>,
    pub path: String,
    pub verdict: String,
    pub expected_event_count: usize,
    pub actual_event_count: usize,
    pub max_error_ms: f64,
    pub mean_error_ms: f64,
    pub p95_error_ms: f64,
    pub failure_category: Option<String>,
    pub issues: Vec<String>,
}

/// Whole timing analysis report.
#[derive(Debug, Clone, PartialEq)]
pub struct TimingAnalysisReport {
    pub scope: String,
    pub source: String,
    pub verdict: String,
    pub threshold_ms: f64,
    pub fixture_count: usize,
    pub passed_count: usize,
    pub failed_count: usize,
    pub analyzed_event_count: usize,
    pub max_error_ms: f64,
    pub mean_error_ms: f64,
    pub p95_error_ms: f64,
    pub failure_categories: Vec<String>,
    pub fixtures: Vec<TimingFixtureResult>,
    pub issues: Vec<String>,
}

/// Minimal headless fixture input accepted by the timing analyzer MVP.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HeadlessTimingFixtureInput {
    pub fixture_id: Option<String>,
    pub path: String,
    pub verdict: String,
    pub note_count: usize,
    pub scheduled_event_count: usize,
    pub hit_count: usize,
    pub miss_count: usize,
    pub song_end_reached: bool,
    pub issues: Vec<String>,
}

/// Minimal headless report input accepted by the timing analyzer MVP.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HeadlessTimingInput {
    pub scope: String,
    pub source: String,
    pub verdict: String,
    pub fixture_count: usize,
    pub total_note_count: usize,
    pub total_scheduled_event_count: usize,
    pub total_hit_count: usize,
    pub total_miss_count: usize,
    pub fixtures: Vec<HeadlessTimingFixtureInput>,
    pub issues: Vec<String>,
}

/// Analyzes Step9 headless evidence using deterministic zero-delta expected
/// timing for perfect autoplay. Later tickets replace this with real chart-time
/// samples and OpenTaiko-compatible threshold policy.
pub fn analyze_headless_input(
    input: &HeadlessTimingInput,
    threshold_ms: f64,
) -> TimingAnalysisReport {
    let fixtures = input
        .fixtures
        .iter()
        .map(|fixture| analyze_fixture(fixture, threshold_ms))
        .collect::<Vec<_>>();
    report_from_fixtures(&input.scope, &input.source, input, threshold_ms, fixtures)
}

/// Parses the deterministic JSON emitted by Step9 headless autoplay into the
/// reduced timing-analyzer input model.
pub fn parse_headless_autoplay_json(text: &str) -> Result<HeadlessTimingInput, TimingError> {
    let scope = string_field(text, "scope").unwrap_or_else(|| "unknown".to_string());
    let verdict = string_field(text, "verdict").unwrap_or_else(|| "fail".to_string());
    let fixture_count = usize_field(text, "fixture_count").unwrap_or(0);
    let total_note_count = usize_field(text, "total_note_count").unwrap_or(0);
    let total_scheduled_event_count = usize_field(text, "total_scheduled_event_count").unwrap_or(0);
    let total_hit_count = usize_field(text, "total_hit_count").unwrap_or(0);
    let total_miss_count = usize_field(text, "total_miss_count").unwrap_or(0);

    if fixture_count == 0 && total_note_count == 0 {
        return Err(TimingError::InvalidInput(
            "input lacks fixture_count and total_note_count fields".to_string(),
        ));
    }

    let fixture = HeadlessTimingFixtureInput {
        fixture_id: None,
        path: scope.clone(),
        verdict: verdict.clone(),
        note_count: total_note_count,
        scheduled_event_count: total_scheduled_event_count,
        hit_count: total_hit_count,
        miss_count: total_miss_count,
        song_end_reached: text.contains("\"song_end_reached\":true") || verdict == "pass",
        issues: Vec::new(),
    };

    Ok(HeadlessTimingInput {
        scope,
        source: "headless_autoplay_json".to_string(),
        verdict,
        fixture_count,
        total_note_count,
        total_scheduled_event_count,
        total_hit_count,
        total_miss_count,
        fixtures: vec![fixture],
        issues: Vec::new(),
    })
}

fn analyze_fixture(fixture: &HeadlessTimingFixtureInput, threshold_ms: f64) -> TimingFixtureResult {
    let expected_event_count = fixture.note_count;
    let actual_event_count = fixture.hit_count;
    let mut issues = Vec::new();
    let mut failure_category = None;

    if fixture.verdict != "pass" {
        failure_category = Some("headless_autoplay_result_error".to_string());
        issues.push(format!("headless fixture verdict is {}", fixture.verdict));
    }
    if fixture.miss_count != 0 {
        failure_category = Some("autoplay_input_error".to_string());
        issues.push(format!("miss_count is {}", fixture.miss_count));
    }
    if !fixture.song_end_reached {
        failure_category = Some("runtime_tick_error".to_string());
        issues.push("song_end_reached is false".to_string());
    }
    if expected_event_count != actual_event_count {
        failure_category = Some("chart_time_error".to_string());
        issues.push(format!(
            "expected_event_count {expected_event_count} does not match actual_event_count {actual_event_count}"
        ));
    }

    let max_error_ms = if issues.is_empty() {
        0.0
    } else {
        threshold_ms + 1.0
    };
    let mean_error_ms = if issues.is_empty() {
        0.0
    } else {
        threshold_ms + 1.0
    };
    let p95_error_ms = if issues.is_empty() {
        0.0
    } else {
        threshold_ms + 1.0
    };

    if max_error_ms > threshold_ms && failure_category.is_none() {
        failure_category = Some("judgement_window_error".to_string());
    }

    let verdict = if issues.is_empty() && max_error_ms <= threshold_ms {
        "pass"
    } else {
        "fail"
    };

    TimingFixtureResult {
        fixture_id: fixture.fixture_id.clone(),
        path: fixture.path.clone(),
        verdict: verdict.to_string(),
        expected_event_count,
        actual_event_count,
        max_error_ms,
        mean_error_ms,
        p95_error_ms,
        failure_category,
        issues,
    }
}

fn report_from_fixtures(
    scope: &str,
    source: &str,
    input: &HeadlessTimingInput,
    threshold_ms: f64,
    fixtures: Vec<TimingFixtureResult>,
) -> TimingAnalysisReport {
    let passed_count = fixtures
        .iter()
        .filter(|fixture| fixture.verdict == "pass")
        .count();
    let failed_count = fixtures.len().saturating_sub(passed_count);
    let analyzed_event_count = fixtures
        .iter()
        .map(|fixture| fixture.actual_event_count)
        .sum();
    let max_error_ms = fixtures
        .iter()
        .map(|fixture| fixture.max_error_ms)
        .fold(0.0_f64, f64::max);
    let mean_error_ms = mean(fixtures.iter().map(|fixture| fixture.mean_error_ms));
    let p95_error_ms = fixtures
        .iter()
        .map(|fixture| fixture.p95_error_ms)
        .fold(0.0_f64, f64::max);
    let mut failure_categories = fixtures
        .iter()
        .filter_map(|fixture| fixture.failure_category.clone())
        .collect::<Vec<_>>();
    failure_categories.sort();
    failure_categories.dedup();

    let mut issues = input.issues.clone();
    if input.verdict != "pass" {
        issues.push(format!(
            "source headless report verdict is {}",
            input.verdict
        ));
    }
    if input.total_miss_count != 0 {
        issues.push(format!(
            "source total_miss_count is {}",
            input.total_miss_count
        ));
    }
    if input.total_hit_count != input.total_note_count {
        issues.push(format!(
            "source total_hit_count {} does not match total_note_count {}",
            input.total_hit_count, input.total_note_count
        ));
    }

    let verdict = if failed_count == 0
        && issues.is_empty()
        && analyzed_event_count > 0
        && max_error_ms <= threshold_ms
    {
        "pass"
    } else {
        "fail"
    };

    TimingAnalysisReport {
        scope: scope.to_string(),
        source: source.to_string(),
        verdict: verdict.to_string(),
        threshold_ms,
        fixture_count: input.fixture_count,
        passed_count,
        failed_count,
        analyzed_event_count,
        max_error_ms,
        mean_error_ms,
        p95_error_ms,
        failure_categories,
        fixtures,
        issues,
    }
}

fn mean(values: impl Iterator<Item = f64>) -> f64 {
    let mut count = 0usize;
    let mut total = 0.0;
    for value in values {
        count += 1;
        total += value;
    }
    if count == 0 {
        0.0
    } else {
        total / count as f64
    }
}

fn string_field(text: &str, name: &str) -> Option<String> {
    let needle = format!("\"{name}\":\"");
    let start = text.find(&needle)? + needle.len();
    let rest = &text[start..];
    let end = rest.find('"')?;
    Some(rest[..end].to_string())
}

fn usize_field(text: &str, name: &str) -> Option<usize> {
    let needle = format!("\"{name}\":");
    let start = text.find(&needle)? + needle.len();
    let rest = &text[start..];
    let digits = rest
        .chars()
        .take_while(|ch| ch.is_ascii_digit())
        .collect::<String>();
    digits.parse().ok()
}

impl TimingAnalysisReport {
    /// Serializes the report as deterministic JSON without external crates.
    #[must_use]
    pub fn to_json(&self) -> String {
        let fixtures = self
            .fixtures
            .iter()
            .map(TimingFixtureResult::to_json)
            .collect::<Vec<_>>()
            .join(",");
        format!(
            "{{\"scope\":\"{}\",\"source\":\"{}\",\"verdict\":\"{}\",\"threshold_ms\":{},\"fixture_count\":{},\"passed_count\":{},\"failed_count\":{},\"analyzed_event_count\":{},\"max_error_ms\":{},\"mean_error_ms\":{},\"p95_error_ms\":{},\"failure_categories\":{},\"fixtures\":[{}],\"issues\":{}}}",
            escape_json(&self.scope),
            escape_json(&self.source),
            escape_json(&self.verdict),
            float_json(self.threshold_ms),
            self.fixture_count,
            self.passed_count,
            self.failed_count,
            self.analyzed_event_count,
            float_json(self.max_error_ms),
            float_json(self.mean_error_ms),
            float_json(self.p95_error_ms),
            string_array_json(&self.failure_categories),
            fixtures,
            string_array_json(&self.issues),
        )
    }

    /// Serializes the report as compact Markdown for terminal use.
    #[must_use]
    pub fn to_markdown(&self) -> String {
        format!(
            "scope: {}\nsource: {}\nverdict: {}\nthreshold_ms: {}\nfixtures: {}\npassed: {}\nfailed: {}\nevents: {}\nmax_error_ms: {}\nmean_error_ms: {}\np95_error_ms: {}\nfailure_categories: {}\nissues: {}",
            self.scope,
            self.source,
            self.verdict,
            float_json(self.threshold_ms),
            self.fixture_count,
            self.passed_count,
            self.failed_count,
            self.analyzed_event_count,
            float_json(self.max_error_ms),
            float_json(self.mean_error_ms),
            float_json(self.p95_error_ms),
            if self.failure_categories.is_empty() { "none".to_string() } else { self.failure_categories.join(", ") },
            if self.issues.is_empty() { "none".to_string() } else { self.issues.join(", ") },
        )
    }
}

impl TimingFixtureResult {
    fn to_json(&self) -> String {
        format!(
            "{{\"fixture_id\":{},\"path\":\"{}\",\"verdict\":\"{}\",\"expected_event_count\":{},\"actual_event_count\":{},\"max_error_ms\":{},\"mean_error_ms\":{},\"p95_error_ms\":{},\"failure_category\":{},\"issues\":{}}}",
            optional_string_json(self.fixture_id.as_deref()),
            escape_json(&self.path),
            escape_json(&self.verdict),
            self.expected_event_count,
            self.actual_event_count,
            float_json(self.max_error_ms),
            float_json(self.mean_error_ms),
            float_json(self.p95_error_ms),
            optional_string_json(self.failure_category.as_deref()),
            string_array_json(&self.issues),
        )
    }
}

fn float_json(value: f64) -> String {
    if value.fract() == 0.0 {
        format!("{value:.1}")
    } else {
        format!("{value:.3}")
    }
}

fn string_array_json(values: &[String]) -> String {
    let items = values
        .iter()
        .map(|value| format!("\"{}\"", escape_json(value)))
        .collect::<Vec<_>>()
        .join(",");
    format!("[{items}]")
}

fn optional_string_json(value: Option<&str>) -> String {
    match value {
        Some(value) => format!("\"{}\"", escape_json(value)),
        None => "null".to_string(),
    }
}

fn escape_json(value: &str) -> String {
    let mut output = String::new();
    for ch in value.chars() {
        match ch {
            '\\' => output.push_str("\\\\"),
            '"' => output.push_str("\\\""),
            '\n' => output.push_str("\\n"),
            '\r' => output.push_str("\\r"),
            '\t' => output.push_str("\\t"),
            other => output.push(other),
        }
    }
    output
}

#[cfg(test)]
mod tests {
    use super::{
        analyze_headless_input, crate_name, HeadlessTimingFixtureInput, HeadlessTimingInput,
    };

    #[test]
    fn exposes_canonical_crate_name() {
        assert_eq!(crate_name(), "taiko_timing");
    }

    #[test]
    fn perfect_headless_input_analyzes_as_zero_error_pass() {
        let input = HeadlessTimingInput {
            scope: "unit".to_string(),
            source: "unit".to_string(),
            verdict: "pass".to_string(),
            fixture_count: 1,
            total_note_count: 4,
            total_scheduled_event_count: 6,
            total_hit_count: 4,
            total_miss_count: 0,
            fixtures: vec![HeadlessTimingFixtureInput {
                fixture_id: Some("FX-UNIT".to_string()),
                path: "unit.tja".to_string(),
                verdict: "pass".to_string(),
                note_count: 4,
                scheduled_event_count: 6,
                hit_count: 4,
                miss_count: 0,
                song_end_reached: true,
                issues: Vec::new(),
            }],
            issues: Vec::new(),
        };
        let report = analyze_headless_input(&input, 1.0);
        assert_eq!(report.verdict, "pass");
        assert_eq!(report.max_error_ms, 0.0);
        assert_eq!(report.analyzed_event_count, 4);
    }
}
