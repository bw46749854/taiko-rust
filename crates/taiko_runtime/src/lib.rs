//! Headless runtime MVP for the OpenTaiko Phase1 autonomous loop.
//!
//! Headless autoplay evidence contract deliberately implements only deterministic, audio-free and render-free
//! perfect autoplay evidence. It converts already-validated TJA fixture structure
//! into a machine-readable playback result that QA Session can pass or reject
//! without manual chart inspection. Full OpenTaiko-compatible timeline, scroll,
//! audio scheduling, judgement windows, score, gauge, branch execution, and
//! timing-log analysis are tracked by the Phase1 feature tickets and the Phase1
//! normal-play compatibility contract.

use std::fmt;
use std::path::Path;

use taiko_chart::{inspect_tja_file, parse_fixture_manifest, ChartError, ManifestFixture};

/// Returns the canonical crate name for workspace and CLI diagnostics.
#[must_use]
pub const fn crate_name() -> &'static str {
    "taiko_runtime"
}

/// Runtime error type for headless autoplay commands.
#[derive(Debug)]
pub enum RuntimeError {
    Chart(ChartError),
    UnsupportedMode(String),
}

impl fmt::Display for RuntimeError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Chart(error) => write!(f, "{error}"),
            Self::UnsupportedMode(mode) => write!(f, "unsupported headless autoplay mode: {mode}"),
        }
    }
}

impl std::error::Error for RuntimeError {}

impl From<ChartError> for RuntimeError {
    fn from(error: ChartError) -> Self {
        Self::Chart(error)
    }
}

/// Supported headless autoplay mode.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HeadlessMode {
    Perfect,
}

impl HeadlessMode {
    /// Parses a CLI mode string.
    pub fn parse(value: &str) -> Result<Self, RuntimeError> {
        match value {
            "perfect" => Ok(Self::Perfect),
            other => Err(RuntimeError::UnsupportedMode(other.to_string())),
        }
    }

    /// Returns the stable JSON/string representation.
    #[must_use]
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Perfect => "perfect",
        }
    }
}

/// Per-fixture headless autoplay result.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HeadlessFixtureResult {
    pub fixture_id: Option<String>,
    pub path: String,
    pub mode: String,
    pub verdict: String,
    pub note_count: usize,
    pub scheduled_event_count: usize,
    pub hit_count: usize,
    pub miss_count: usize,
    pub song_end_reached: bool,
    pub chart_verdict: String,
    pub issues: Vec<String>,
}

/// Headless autoplay report for one chart or a manifest.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HeadlessAutoplayReport {
    pub scope: String,
    pub mode: String,
    pub verdict: String,
    pub fixture_count: usize,
    pub passed_count: usize,
    pub failed_count: usize,
    pub total_note_count: usize,
    pub total_scheduled_event_count: usize,
    pub total_hit_count: usize,
    pub total_miss_count: usize,
    pub fixtures: Vec<HeadlessFixtureResult>,
    pub issues: Vec<String>,
}

/// Runs perfect headless autoplay for one chart.
pub fn autoplay_chart(
    path: &Path,
    mode: HeadlessMode,
) -> Result<HeadlessAutoplayReport, RuntimeError> {
    let fixture = run_fixture(None, path, &path.to_string_lossy(), mode)?;
    Ok(report_from_fixtures(
        path.to_string_lossy().as_ref(),
        mode,
        vec![fixture],
        Vec::new(),
    ))
}

/// Runs perfect headless autoplay for all manifest fixtures marked headless-required.
pub fn autoplay_manifest(
    root: &Path,
    manifest_path: &Path,
    mode: HeadlessMode,
) -> Result<HeadlessAutoplayReport, RuntimeError> {
    let text = std::fs::read_to_string(manifest_path).map_err(|source| {
        RuntimeError::Chart(ChartError::Io {
            path: manifest_path.to_path_buf(),
            source,
        })
    })?;
    let manifest = parse_fixture_manifest(&text)?;
    let mut fixtures = Vec::new();
    let mut issues = Vec::new();

    for entry in manifest
        .fixtures
        .iter()
        .filter(|fixture| fixture.headless_required)
    {
        let absolute = root.join(&entry.path);
        match run_manifest_fixture(entry, &absolute, mode) {
            Ok(result) => fixtures.push(result),
            Err(error) => {
                issues.push(format!("{}: {}", entry.fixture_id, error));
                fixtures.push(HeadlessFixtureResult {
                    fixture_id: Some(entry.fixture_id.clone()),
                    path: entry.path.clone(),
                    mode: mode.as_str().to_string(),
                    verdict: "fail".to_string(),
                    note_count: 0,
                    scheduled_event_count: 0,
                    hit_count: 0,
                    miss_count: 0,
                    song_end_reached: false,
                    chart_verdict: "error".to_string(),
                    issues: vec![error.to_string()],
                });
            }
        }
    }

    Ok(report_from_fixtures(
        &relative_display(root, manifest_path),
        mode,
        fixtures,
        issues,
    ))
}

fn run_manifest_fixture(
    entry: &ManifestFixture,
    absolute_path: &Path,
    mode: HeadlessMode,
) -> Result<HeadlessFixtureResult, RuntimeError> {
    run_fixture(
        Some(entry.fixture_id.clone()),
        absolute_path,
        &entry.path,
        mode,
    )
}

fn run_fixture(
    fixture_id: Option<String>,
    path: &Path,
    display_path: &str,
    mode: HeadlessMode,
) -> Result<HeadlessFixtureResult, RuntimeError> {
    let inspection = inspect_tja_file(path)?;
    let mut issues = inspection
        .issues
        .iter()
        .filter(|issue| issue.severity == "error")
        .map(|issue| format!("{}: {}", issue.code, issue.message))
        .collect::<Vec<_>>();

    let chart_passed = inspection.verdict == "pass";
    let note_count = if chart_passed {
        inspection.note_token_count
    } else {
        0
    };
    let scheduled_event_count = if chart_passed { note_count + 2 } else { 0 };
    let (hit_count, miss_count, song_end_reached) = match mode {
        HeadlessMode::Perfect if chart_passed => (note_count, 0, true),
        HeadlessMode::Perfect => (0, note_count, false),
    };

    if chart_passed && note_count == 0 {
        issues.push("headless_no_scheduled_notes".to_string());
    }

    let verdict = if chart_passed && miss_count == 0 && song_end_reached && note_count > 0 {
        "pass"
    } else {
        "fail"
    };

    Ok(HeadlessFixtureResult {
        fixture_id,
        path: display_path.to_string(),
        mode: mode.as_str().to_string(),
        verdict: verdict.to_string(),
        note_count,
        scheduled_event_count,
        hit_count,
        miss_count,
        song_end_reached,
        chart_verdict: inspection.verdict,
        issues,
    })
}

fn report_from_fixtures(
    scope: &str,
    mode: HeadlessMode,
    fixtures: Vec<HeadlessFixtureResult>,
    issues: Vec<String>,
) -> HeadlessAutoplayReport {
    let fixture_count = fixtures.len();
    let passed_count = fixtures
        .iter()
        .filter(|fixture| fixture.verdict == "pass")
        .count();
    let failed_count = fixture_count.saturating_sub(passed_count);
    let total_note_count = fixtures.iter().map(|fixture| fixture.note_count).sum();
    let total_scheduled_event_count = fixtures
        .iter()
        .map(|fixture| fixture.scheduled_event_count)
        .sum();
    let total_hit_count = fixtures.iter().map(|fixture| fixture.hit_count).sum();
    let total_miss_count = fixtures.iter().map(|fixture| fixture.miss_count).sum();
    let verdict = if failed_count == 0 && issues.is_empty() && fixture_count > 0 {
        "pass"
    } else {
        "fail"
    };

    HeadlessAutoplayReport {
        scope: scope.to_string(),
        mode: mode.as_str().to_string(),
        verdict: verdict.to_string(),
        fixture_count,
        passed_count,
        failed_count,
        total_note_count,
        total_scheduled_event_count,
        total_hit_count,
        total_miss_count,
        fixtures,
        issues,
    }
}

impl HeadlessAutoplayReport {
    /// Serializes the report as deterministic JSON without external crates.
    #[must_use]
    pub fn to_json(&self) -> String {
        let fixtures = self
            .fixtures
            .iter()
            .map(HeadlessFixtureResult::to_json)
            .collect::<Vec<_>>()
            .join(",");
        format!(
            "{{\"scope\":\"{}\",\"mode\":\"{}\",\"verdict\":\"{}\",\"fixture_count\":{},\"passed_count\":{},\"failed_count\":{},\"total_note_count\":{},\"total_scheduled_event_count\":{},\"total_hit_count\":{},\"total_miss_count\":{},\"fixtures\":[{}],\"issues\":{}}}",
            escape_json(&self.scope),
            escape_json(&self.mode),
            escape_json(&self.verdict),
            self.fixture_count,
            self.passed_count,
            self.failed_count,
            self.total_note_count,
            self.total_scheduled_event_count,
            self.total_hit_count,
            self.total_miss_count,
            fixtures,
            string_array_json(&self.issues),
        )
    }

    /// Serializes the report as compact Markdown for terminal use.
    #[must_use]
    pub fn to_markdown(&self) -> String {
        format!(
            "scope: {}\nmode: {}\nverdict: {}\nfixtures: {}\npassed: {}\nfailed: {}\nnotes: {}\nhits: {}\nmisses: {}\nissues: {}",
            self.scope,
            self.mode,
            self.verdict,
            self.fixture_count,
            self.passed_count,
            self.failed_count,
            self.total_note_count,
            self.total_hit_count,
            self.total_miss_count,
            if self.issues.is_empty() {
                "none".to_string()
            } else {
                self.issues.join(", ")
            }
        )
    }
}

impl HeadlessFixtureResult {
    fn to_json(&self) -> String {
        format!(
            "{{\"fixture_id\":{},\"path\":\"{}\",\"mode\":\"{}\",\"verdict\":\"{}\",\"note_count\":{},\"scheduled_event_count\":{},\"hit_count\":{},\"miss_count\":{},\"song_end_reached\":{},\"chart_verdict\":\"{}\",\"issues\":{}}}",
            optional_string_json(self.fixture_id.as_deref()),
            escape_json(&self.path),
            escape_json(&self.mode),
            escape_json(&self.verdict),
            self.note_count,
            self.scheduled_event_count,
            self.hit_count,
            self.miss_count,
            self.song_end_reached,
            escape_json(&self.chart_verdict),
            string_array_json(&self.issues),
        )
    }
}

fn relative_display(root: &Path, path: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .replace('\\', "/")
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
    use super::{crate_name, report_from_fixtures, HeadlessFixtureResult, HeadlessMode};

    #[test]
    fn exposes_canonical_crate_name() {
        assert_eq!(crate_name(), "taiko_runtime");
    }

    #[test]
    fn perfect_report_passes_when_all_fixtures_pass() {
        let report = report_from_fixtures(
            "unit",
            HeadlessMode::Perfect,
            vec![HeadlessFixtureResult {
                fixture_id: Some("FX-UNIT".to_string()),
                path: "unit.tja".to_string(),
                mode: "perfect".to_string(),
                verdict: "pass".to_string(),
                note_count: 4,
                scheduled_event_count: 6,
                hit_count: 4,
                miss_count: 0,
                song_end_reached: true,
                chart_verdict: "pass".to_string(),
                issues: Vec::new(),
            }],
            Vec::new(),
        );
        assert_eq!(report.verdict, "pass");
        assert_eq!(report.total_hit_count, 4);
        assert_eq!(report.total_miss_count, 0);
    }
}
