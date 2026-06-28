//! Phase1 synthetic fixture validation support.
//!
//! Fixture validation command surface intentionally implements only the parser surface needed for autonomous
//! fixture validation. Full OpenTaiko-compatible scheduling, branch execution,
//! scoring, judgement, rendering, and audio behavior are tracked by the Phase1
//! feature tickets and the Phase1 normal-play compatibility contract.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt;
use std::fs;
use std::io;
use std::path::{Path, PathBuf};

/// Returns the canonical crate name for workspace and CLI diagnostics.
#[must_use]
pub const fn crate_name() -> &'static str {
    "taiko_chart"
}

/// Error type for fixture and chart validation.
#[derive(Debug)]
pub enum ChartError {
    Io { path: PathBuf, source: io::Error },
    Manifest(String),
}

impl fmt::Display for ChartError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io { path, source } => write!(f, "{}: {}", path.display(), source),
            Self::Manifest(message) => write!(f, "manifest error: {message}"),
        }
    }
}

impl std::error::Error for ChartError {}

/// One fixture entry declared in the synthetic manifest.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ManifestFixture {
    pub fixture_id: String,
    pub path: String,
    pub primary_target: String,
    pub headless_required: bool,
}

/// Parsed synthetic fixture manifest.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FixtureManifest {
    pub schema_version: String,
    pub declared_fixture_count: usize,
    pub fixtures: Vec<ManifestFixture>,
}

/// One validation issue.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidationIssue {
    pub severity: String,
    pub code: String,
    pub message: String,
    pub line: Option<usize>,
}

impl ValidationIssue {
    #[must_use]
    pub fn error(code: &str, message: impl Into<String>, line: Option<usize>) -> Self {
        Self {
            severity: "error".to_string(),
            code: code.to_string(),
            message: message.into(),
            line,
        }
    }

    #[must_use]
    pub fn warning(code: &str, message: impl Into<String>, line: Option<usize>) -> Self {
        Self {
            severity: "warning".to_string(),
            code: code.to_string(),
            message: message.into(),
            line,
        }
    }
}

/// Basic chart inspection report for a TJA file.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ChartInspectionReport {
    pub path: String,
    pub verdict: String,
    pub title: Option<String>,
    pub courses: Vec<String>,
    pub header_count: usize,
    pub command_count: usize,
    pub classified_command_count: usize,
    pub unknown_commands: Vec<String>,
    pub start_count: usize,
    pub end_count: usize,
    pub measure_count: usize,
    pub digit_token_count: usize,
    pub note_token_count: usize,
    pub issues: Vec<ValidationIssue>,
}

/// One fixture's manifest-level validation result.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FixtureValidationItem {
    pub fixture_id: String,
    pub path: String,
    pub exists: bool,
    pub verdict: String,
    pub issue_count: usize,
    pub inspection: Option<ChartInspectionReport>,
}

/// Whole-manifest validation report.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FixtureValidationReport {
    pub manifest_path: String,
    pub verdict: String,
    pub declared_fixture_count: usize,
    pub manifest_entry_count: usize,
    pub validated_count: usize,
    pub missing_count: usize,
    pub invalid_count: usize,
    pub duplicate_fixture_ids: Vec<String>,
    pub fixtures: Vec<FixtureValidationItem>,
    pub issues: Vec<ValidationIssue>,
}

/// Parses the synthetic manifest subset required by the fixture validation command surface.
pub fn parse_fixture_manifest(text: &str) -> Result<FixtureManifest, ChartError> {
    let mut schema_version = String::new();
    let mut declared_fixture_count = 0usize;
    let mut fixtures = Vec::new();
    let mut current: Option<ManifestFixtureBuilder> = None;

    for (index, raw_line) in text.lines().enumerate() {
        let line_no = index + 1;
        let line = strip_toml_comment(raw_line).trim();
        if line.is_empty() || line == "[asset_policy]" {
            continue;
        }
        if line == "[[fixtures]]" {
            if let Some(builder) = current.take() {
                fixtures.push(builder.finish(line_no)?);
            }
            current = Some(ManifestFixtureBuilder::default());
            continue;
        }
        let Some((key, value)) = parse_key_value(line) else {
            continue;
        };
        if let Some(builder) = current.as_mut() {
            match key {
                "fixture_id" => builder.fixture_id = parse_string(value),
                "path" => builder.path = parse_string(value),
                "primary_target" => builder.primary_target = parse_string(value),
                "headless_required" => builder.headless_required = parse_bool(value),
                _ => {}
            }
        } else {
            match key {
                "schema_version" => schema_version = parse_string(value).unwrap_or_default(),
                "fixture_count" => {
                    declared_fixture_count = value.trim().parse::<usize>().map_err(|_| {
                        ChartError::Manifest(format!("invalid fixture_count at line {line_no}"))
                    })?;
                }
                _ => {}
            }
        }
    }

    if let Some(builder) = current.take() {
        fixtures.push(builder.finish(text.lines().count())?);
    }

    if schema_version.is_empty() {
        return Err(ChartError::Manifest("missing schema_version".to_string()));
    }
    if declared_fixture_count == 0 {
        return Err(ChartError::Manifest("missing fixture_count".to_string()));
    }

    Ok(FixtureManifest {
        schema_version,
        declared_fixture_count,
        fixtures,
    })
}

#[derive(Debug, Default)]
struct ManifestFixtureBuilder {
    fixture_id: Option<String>,
    path: Option<String>,
    primary_target: Option<String>,
    headless_required: Option<bool>,
}

impl ManifestFixtureBuilder {
    fn finish(self, line_no: usize) -> Result<ManifestFixture, ChartError> {
        Ok(ManifestFixture {
            fixture_id: self.fixture_id.ok_or_else(|| {
                ChartError::Manifest(format!(
                    "fixture entry ending near line {line_no} lacks fixture_id"
                ))
            })?,
            path: self.path.ok_or_else(|| {
                ChartError::Manifest(format!(
                    "fixture entry ending near line {line_no} lacks path"
                ))
            })?,
            primary_target: self.primary_target.unwrap_or_default(),
            headless_required: self.headless_required.unwrap_or(false),
        })
    }
}

/// Validates all fixtures declared by a synthetic manifest.
pub fn validate_fixture_manifest(
    root: &Path,
    manifest_path: &Path,
) -> Result<FixtureValidationReport, ChartError> {
    let manifest_text = read_text(manifest_path)?;
    let manifest = parse_fixture_manifest(&manifest_text)?;
    let mut issues = Vec::new();
    let mut fixtures = Vec::new();
    let mut seen = BTreeSet::new();
    let mut duplicates = Vec::new();
    let mut validated_count = 0usize;
    let mut missing_count = 0usize;
    let mut invalid_count = 0usize;

    if manifest.declared_fixture_count != manifest.fixtures.len() {
        issues.push(ValidationIssue::error(
            "manifest_count_mismatch",
            format!(
                "declared fixture_count {} does not match {} entries",
                manifest.declared_fixture_count,
                manifest.fixtures.len()
            ),
            None,
        ));
    }

    for entry in &manifest.fixtures {
        if !seen.insert(entry.fixture_id.clone()) {
            duplicates.push(entry.fixture_id.clone());
        }
        let absolute = root.join(&entry.path);
        if !absolute.is_file() {
            missing_count += 1;
            fixtures.push(FixtureValidationItem {
                fixture_id: entry.fixture_id.clone(),
                path: entry.path.clone(),
                exists: false,
                verdict: "fail".to_string(),
                issue_count: 1,
                inspection: None,
            });
            continue;
        }

        let inspection = inspect_tja_file_with_display(&absolute, &entry.path)?;
        let is_pass = inspection.verdict == "pass";
        if is_pass {
            validated_count += 1;
        } else {
            invalid_count += 1;
        }
        fixtures.push(FixtureValidationItem {
            fixture_id: entry.fixture_id.clone(),
            path: entry.path.clone(),
            exists: true,
            verdict: if is_pass { "pass" } else { "fail" }.to_string(),
            issue_count: inspection.issues.len(),
            inspection: Some(inspection),
        });
    }

    if !duplicates.is_empty() {
        issues.push(ValidationIssue::error(
            "duplicate_fixture_id",
            format!("duplicate fixture ids: {}", duplicates.join(", ")),
            None,
        ));
    }

    let verdict = if issues.iter().any(|issue| issue.severity == "error")
        || missing_count > 0
        || invalid_count > 0
    {
        "fail"
    } else {
        "pass"
    };

    Ok(FixtureValidationReport {
        manifest_path: relative_display(root, manifest_path),
        verdict: verdict.to_string(),
        declared_fixture_count: manifest.declared_fixture_count,
        manifest_entry_count: manifest.fixtures.len(),
        validated_count,
        missing_count,
        invalid_count,
        duplicate_fixture_ids: duplicates,
        fixtures,
        issues,
    })
}

/// Inspects one TJA fixture path.
pub fn inspect_tja_file(path: &Path) -> Result<ChartInspectionReport, ChartError> {
    inspect_tja_file_with_display(path, &path.to_string_lossy())
}

fn inspect_tja_file_with_display(
    path: &Path,
    display_path: &str,
) -> Result<ChartInspectionReport, ChartError> {
    let text = read_text(path)?;
    Ok(inspect_tja_text(display_path, &text))
}

/// Inspects TJA text without requiring a filesystem path.
#[must_use]
pub fn inspect_tja_text(path: &str, text: &str) -> ChartInspectionReport {
    let mut issues = Vec::new();
    let mut headers = BTreeMap::<String, String>::new();
    let mut courses = Vec::new();
    let mut command_count = 0usize;
    let mut classified_command_count = 0usize;
    let mut unknown_commands = BTreeSet::<String>::new();
    let mut start_count = 0usize;
    let mut end_count = 0usize;
    let mut measure_count = 0usize;
    let mut digit_token_count = 0usize;
    let mut note_token_count = 0usize;
    let mut inside_chart = false;

    for (index, raw_line) in text.lines().enumerate() {
        let line_no = index + 1;
        let line = strip_tja_comment(raw_line).trim();
        if line.is_empty() {
            continue;
        }

        if line.starts_with('#') {
            command_count += 1;
            let command = command_name(line);
            if is_known_tja_command(command) {
                classified_command_count += 1;
            } else {
                unknown_commands.insert(command.to_string());
                issues.push(ValidationIssue::error(
                    "unknown_command",
                    format!("unknown TJA command {command}"),
                    Some(line_no),
                ));
            }
            match command {
                "#START" => {
                    start_count += 1;
                    inside_chart = true;
                }
                "#END" => {
                    end_count += 1;
                    inside_chart = false;
                }
                _ => {}
            }
            continue;
        }

        if let Some((key, value)) = line.split_once(':') {
            let key = key.trim().to_ascii_uppercase();
            let value = value.trim().to_string();
            if key == "COURSE" {
                courses.push(value.clone());
            }
            headers.entry(key).or_insert(value);
            continue;
        }

        if inside_chart {
            for character in line.chars() {
                match character {
                    '0'..='9' => {
                        digit_token_count += 1;
                        if character != '0' {
                            note_token_count += 1;
                        }
                    }
                    'A'..='Z' => {
                        note_token_count += 1;
                    }
                    ',' => measure_count += 1,
                    ' ' | '\t' => {}
                    other => issues.push(ValidationIssue::error(
                        "invalid_chart_token",
                        format!("invalid chart token {other:?}"),
                        Some(line_no),
                    )),
                }
            }
        } else {
            issues.push(ValidationIssue::warning(
                "ignored_non_header_line",
                "non-header text outside #START/#END was ignored",
                Some(line_no),
            ));
        }
    }

    for required in ["TITLE", "BPM", "WAVE", "COURSE", "LEVEL"] {
        if !headers.contains_key(required) {
            issues.push(ValidationIssue::error(
                "missing_required_header",
                format!("missing required header {required}"),
                None,
            ));
        }
    }
    if start_count == 0 {
        issues.push(ValidationIssue::error(
            "missing_start",
            "missing #START",
            None,
        ));
    }
    if end_count == 0 {
        issues.push(ValidationIssue::error("missing_end", "missing #END", None));
    }
    if end_count < start_count {
        issues.push(ValidationIssue::error(
            "unbalanced_start_end",
            format!("#END count {end_count} is less than #START count {start_count}"),
            None,
        ));
    }
    if note_token_count == 0 {
        issues.push(ValidationIssue::error(
            "no_note_tokens",
            "chart contains no non-zero note tokens",
            None,
        ));
    }

    let verdict = if issues.iter().any(|issue| issue.severity == "error") {
        "fail"
    } else {
        "pass"
    };

    ChartInspectionReport {
        path: path.to_string(),
        verdict: verdict.to_string(),
        title: headers.get("TITLE").cloned(),
        courses,
        header_count: headers.len(),
        command_count,
        classified_command_count,
        unknown_commands: unknown_commands.into_iter().collect(),
        start_count,
        end_count,
        measure_count,
        digit_token_count,
        note_token_count,
        issues,
    }
}

fn read_text(path: &Path) -> Result<String, ChartError> {
    fs::read_to_string(path).map_err(|source| ChartError::Io {
        path: path.to_path_buf(),
        source,
    })
}

fn parse_key_value(line: &str) -> Option<(&str, &str)> {
    line.split_once('=')
        .map(|(key, value)| (key.trim(), value.trim()))
}

fn parse_string(value: &str) -> Option<String> {
    let value = value.trim();
    if value.starts_with('"') && value.ends_with('"') && value.len() >= 2 {
        Some(value[1..value.len() - 1].to_string())
    } else {
        None
    }
}

fn parse_bool(value: &str) -> Option<bool> {
    match value.trim() {
        "true" => Some(true),
        "false" => Some(false),
        _ => None,
    }
}

fn strip_toml_comment(line: &str) -> &str {
    line.split('#').next().unwrap_or(line)
}

fn strip_tja_comment(line: &str) -> &str {
    line.split("//").next().unwrap_or(line)
}

fn command_name(line: &str) -> &str {
    line.split_whitespace()
        .next()
        .unwrap_or(line)
        .split(':')
        .next()
        .unwrap_or(line)
}

fn is_known_tja_command(command: &str) -> bool {
    matches!(
        command,
        "#START"
            | "#END"
            | "#BPMCHANGE"
            | "#MEASURE"
            | "#DELAY"
            | "#SCROLL"
            | "#GOGOSTART"
            | "#GOGOEND"
            | "#BARLINE"
            | "#BARLINEON"
            | "#BARLINEOFF"
            | "#BRANCHSTART"
            | "#BRANCHEND"
            | "#SECTION"
            | "#LEVELHOLD"
            | "#N"
            | "#E"
            | "#M"
            | "#BMSCROLL"
            | "#HBSCROLL"
            | "#NMSCROLL"
            | "#SUDDEN"
            | "#DIRECTION"
            | "#JPOSSCROLL"
            | "#NEXTSONG"
            | "#BGAON"
            | "#CAMZOOM"
            | "#LYRIC"
    )
}

fn relative_display(root: &Path, path: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .replace('\\', "/")
}

impl ChartInspectionReport {
    #[must_use]
    pub fn to_json(&self) -> String {
        format!(
            "{{\"path\":\"{}\",\"verdict\":\"{}\",\"title\":{},\"courses\":{},\"header_count\":{},\"command_count\":{},\"classified_command_count\":{},\"unknown_commands\":{},\"start_count\":{},\"end_count\":{},\"measure_count\":{},\"digit_token_count\":{},\"note_token_count\":{},\"issues\":{}}}",
            escape_json(&self.path),
            escape_json(&self.verdict),
            optional_string_json(self.title.as_deref()),
            string_array_json(&self.courses),
            self.header_count,
            self.command_count,
            self.classified_command_count,
            string_array_json(&self.unknown_commands),
            self.start_count,
            self.end_count,
            self.measure_count,
            self.digit_token_count,
            self.note_token_count,
            issues_json(&self.issues)
        )
    }

    #[must_use]
    pub fn to_markdown(&self) -> String {
        format!(
            "fixture: {}\nverdict: {}\ntitle: {}\ncourses: {}\nnotes: {}\ncommands: {}/{} classified\nissues: {}",
            self.path,
            self.verdict,
            self.title.as_deref().unwrap_or("none"),
            self.courses.join(", "),
            self.note_token_count,
            self.classified_command_count,
            self.command_count,
            self.issues.len()
        )
    }
}

impl FixtureValidationReport {
    #[must_use]
    pub fn to_json(&self) -> String {
        let fixtures = self
            .fixtures
            .iter()
            .map(FixtureValidationItem::to_json)
            .collect::<Vec<_>>()
            .join(",");
        format!(
            "{{\"manifest_path\":\"{}\",\"verdict\":\"{}\",\"declared_fixture_count\":{},\"manifest_entry_count\":{},\"validated_count\":{},\"missing_count\":{},\"invalid_count\":{},\"duplicate_fixture_ids\":{},\"fixtures\":[{}],\"issues\":{}}}",
            escape_json(&self.manifest_path),
            escape_json(&self.verdict),
            self.declared_fixture_count,
            self.manifest_entry_count,
            self.validated_count,
            self.missing_count,
            self.invalid_count,
            string_array_json(&self.duplicate_fixture_ids),
            fixtures,
            issues_json(&self.issues)
        )
    }

    #[must_use]
    pub fn to_markdown(&self) -> String {
        format!(
            "manifest: {}\nverdict: {}\nvalidated: {}/{}\nmissing: {}\ninvalid: {}\nduplicate fixture ids: {}",
            self.manifest_path,
            self.verdict,
            self.validated_count,
            self.manifest_entry_count,
            self.missing_count,
            self.invalid_count,
            if self.duplicate_fixture_ids.is_empty() {
                "none".to_string()
            } else {
                self.duplicate_fixture_ids.join(", ")
            }
        )
    }
}

impl FixtureValidationItem {
    fn to_json(&self) -> String {
        let inspection = self
            .inspection
            .as_ref()
            .map(ChartInspectionReport::to_json)
            .unwrap_or_else(|| "null".to_string());
        format!(
            "{{\"fixture_id\":\"{}\",\"path\":\"{}\",\"exists\":{},\"verdict\":\"{}\",\"issue_count\":{},\"inspection\":{}}}",
            escape_json(&self.fixture_id),
            escape_json(&self.path),
            self.exists,
            escape_json(&self.verdict),
            self.issue_count,
            inspection
        )
    }
}

fn issues_json(issues: &[ValidationIssue]) -> String {
    let values = issues
        .iter()
        .map(|issue| {
            format!(
                "{{\"severity\":\"{}\",\"code\":\"{}\",\"message\":\"{}\",\"line\":{}}}",
                escape_json(&issue.severity),
                escape_json(&issue.code),
                escape_json(&issue.message),
                issue
                    .line
                    .map_or_else(|| "null".to_string(), |line| line.to_string())
            )
        })
        .collect::<Vec<_>>()
        .join(",");
    format!("[{values}]")
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
    use super::{crate_name, inspect_tja_text, parse_fixture_manifest};

    #[test]
    fn exposes_canonical_crate_name() {
        assert_eq!(crate_name(), "taiko_chart");
    }

    #[test]
    fn parses_manifest_fixture_entries() {
        let text = r#"
schema_version = "phase1-synthetic-manifest/v1"
fixture_count = 1

[[fixtures]]
fixture_id = "FX-TEST-001"
path = "fixtures/synthetic/test.tja"
primary_target = "test"
headless_required = true
"#;
        let manifest = parse_fixture_manifest(text).expect("manifest parses");
        assert_eq!(manifest.declared_fixture_count, 1);
        assert_eq!(manifest.fixtures[0].fixture_id, "FX-TEST-001");
        assert!(manifest.fixtures[0].headless_required);
    }

    #[test]
    fn inspects_minimal_tja() {
        let text =
            "TITLE:Unit\nBPM:120\nWAVE:__dummy__.ogg\nCOURSE:Oni\nLEVEL:1\n#START\n1111,\n#END\n";
        let report = inspect_tja_text("unit.tja", text);
        assert_eq!(report.verdict, "pass");
        assert_eq!(report.note_token_count, 4);
        assert_eq!(report.start_count, 1);
        assert_eq!(report.end_count, 1);
    }
}
