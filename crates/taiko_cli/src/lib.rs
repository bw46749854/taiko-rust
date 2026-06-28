//! Machine-readable loop orchestration support for the OpenTaiko Phase1 package.

use std::collections::BTreeMap;
use std::env;
use std::fmt;
use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use taiko_chart::{inspect_tja_file, validate_fixture_manifest};
use taiko_runtime::{autoplay_chart, autoplay_manifest, HeadlessAutoplayReport, HeadlessMode};
use taiko_test_support::{list_markdown_files, read_utf8};
use taiko_timing::{
    analyze_headless_input, parse_headless_autoplay_json, HeadlessTimingFixtureInput,
    HeadlessTimingInput, TimingAnalysisReport,
};

/// CLI result type.
pub type CliResult<T> = Result<T, CliError>;

/// Error type used by the CLI without external dependencies.
#[derive(Debug)]
pub enum CliError {
    Io { path: PathBuf, source: io::Error },
    Usage(String),
    MissingProjectRoot(PathBuf),
    UnknownGate(String),
    Chart(String),
    Runtime(String),
    Timing(String),
    Failure(String),
    Qa(String),
    Phase1(String),
    Loop(String),
}

impl fmt::Display for CliError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io { path, source } => write!(f, "{}: {}", path.display(), source),
            Self::Usage(message) => write!(f, "{message}"),
            Self::MissingProjectRoot(path) => write!(
                f,
                "could not locate project root from {}: missing AGENTS.md and .loop",
                path.display()
            ),
            Self::UnknownGate(gate) => write!(f, "unknown gate: {gate}"),
            Self::Chart(message) => write!(f, "{message}"),
            Self::Runtime(message) => write!(f, "{message}"),
            Self::Timing(message) => write!(f, "{message}"),
            Self::Failure(message) => write!(f, "{message}"),
            Self::Qa(message) => write!(f, "{message}"),
            Self::Phase1(message) => write!(f, "{message}"),
            Self::Loop(message) => write!(f, "{message}"),
        }
    }
}

impl std::error::Error for CliError {}

impl From<taiko_chart::ChartError> for CliError {
    fn from(error: taiko_chart::ChartError) -> Self {
        Self::Chart(error.to_string())
    }
}

impl From<taiko_runtime::RuntimeError> for CliError {
    fn from(error: taiko_runtime::RuntimeError) -> Self {
        Self::Runtime(error.to_string())
    }
}

impl From<taiko_timing::TimingError> for CliError {
    fn from(error: taiko_timing::TimingError) -> Self {
        Self::Timing(error.to_string())
    }
}

/// Parsed ticket summary.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Ticket {
    pub id: String,
    pub title: String,
    pub status: String,
    pub owner_session: String,
    pub review_session: String,
    pub dependencies: Vec<String>,
    pub required_checks: Vec<String>,
    pub evidence_requirements: Vec<String>,
    pub path: String,
}

/// Parsed gate summary.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Gate {
    pub id: String,
    pub title: String,
    pub status: String,
    pub owner: String,
    pub reviewer: String,
    pub scorecard_impact: Vec<String>,
    pub required_inputs: Vec<String>,
    pub pass_criteria: Vec<String>,
    pub output_path: String,
    pub next_ticket_transition: String,
    pub path: String,
}

/// Gate dry-run verdict.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GateVerdict {
    pub gate_id: String,
    pub verdict: String,
    pub missing_inputs: Vec<String>,
    pub present_inputs: Vec<String>,
    pub pass_criteria_count: usize,
}

/// Loop status report.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LoopStatus {
    pub autonomy_score_estimate: u32,
    pub ready_tickets: Vec<String>,
    pub blocked_tickets: Vec<String>,
    pub done_tickets: Vec<String>,
    pub missing_gate_evidence: Vec<String>,
    pub next_selected_ticket: Option<String>,
    pub open_failures: Vec<String>,
}

/// Step17 loop-controller run-once plan.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LoopRunOncePlan {
    pub run_id: String,
    pub mode: String,
    pub state: String,
    pub verdict: String,
    pub selected_ticket: Option<String>,
    pub next_action: String,
    pub reason: String,
    pub branch: Option<String>,
    pub implementation_worktree: Option<String>,
    pub review_worktree: Option<String>,
    pub qa_worktree: Option<String>,
    pub session_metadata_path: Option<String>,
    pub controller_report_json: String,
    pub controller_report_markdown: String,
    pub next_codex_prompt: String,
    pub required_commands: Vec<String>,
    pub missing_gate_evidence: Vec<String>,
    pub open_failures: Vec<String>,
    pub artifacts_written: Vec<String>,
}

pub const SUPPORTED_COMMAND_SURFACE: &[&str] = &[
    "loop inspect tickets",
    "loop inspect gates",
    "loop next",
    "loop run-once --mode plan",
    "loop run-once --mode apply",
    "loop metadata validate",
    "loop gate GATE-0000 --dry-run",
    "loop report status",
    "fixture validate --manifest",
    "fixture inspect",
    "headless autoplay --chart",
    "headless autoplay --manifest",
    "timing analyze --input",
    "timing analyze --manifest",
    "timing_log_analyzer --input",
    "loop failure ingest",
    "loop failure classify",
    "loop ticket propose --from-failure",
    "loop ticket materialize --from-failure",
    "loop ticket validate",
    "loop retry-budget check",
    "qa run",
    "qa compare",
    "qa verdict",
    "phase1 feature validate",
    "phase1 feature plan",
    "--from-failure",
    "--threshold-ms",
    "--mode perfect",
    "--format json",
];

/// Entry point used by the `taiko_cli` binary.
pub fn run_cli(args: &[String]) -> CliResult<String> {
    let options = parse_options(args)?;
    let root = locate_project_root(env::current_dir().map_err(|source| CliError::Io {
        path: PathBuf::from("."),
        source,
    })?)?;

    if options.words.is_empty() {
        return Err(CliError::Usage(usage()));
    }

    match options.words.as_slice() {
        [loop_word, inspect_word, subject]
            if loop_word == "loop" && inspect_word == "inspect" && subject == "tickets" =>
        {
            let tickets = load_tickets(&root)?;
            Ok(render_tickets(&tickets, options.format))
        }
        [loop_word, inspect_word, subject]
            if loop_word == "loop" && inspect_word == "inspect" && subject == "gates" =>
        {
            let gates = load_gates(&root)?;
            Ok(render_gates(&gates, options.format))
        }
        [loop_word, next_word] if loop_word == "loop" && next_word == "next" => {
            let tickets = load_tickets(&root)?;
            let gates = load_gates(&root)?;
            Ok(render_next(
                &select_next_ticket(&tickets, &gates, &root),
                options.format,
            ))
        }
        [loop_word, gate_word, gate_id]
            if loop_word == "loop" && gate_word == "gate" && options.dry_run =>
        {
            let gates = load_gates(&root)?;
            let gate = gates
                .iter()
                .find(|candidate| candidate.id == *gate_id)
                .ok_or_else(|| CliError::UnknownGate(gate_id.to_string()))?;
            let verdict = dry_run_gate(&root, gate);
            Ok(render_gate_verdict(&verdict, options.format))
        }
        [loop_word, run_once_word] if loop_word == "loop" && run_once_word == "run-once" => {
            let mode = options.mode.as_deref().unwrap_or("plan");
            let plan = build_loop_run_once_plan(&root, mode)?;
            let plan = if mode == "apply" {
                apply_loop_run_once_plan(&root, plan)?
            } else {
                plan
            };
            Ok(render_loop_run_once_plan(&plan, options.format))
        }
        [loop_word, report_word, status_word]
            if loop_word == "loop" && report_word == "report" && status_word == "status" =>
        {
            let tickets = load_tickets(&root)?;
            let gates = load_gates(&root)?;
            let status = build_status(&root, &tickets, &gates);
            Ok(render_status(&status, options.format))
        }
        [fixture_word, validate_word]
            if fixture_word == "fixture" && validate_word == "validate" =>
        {
            let manifest = options
                .manifest
                .clone()
                .unwrap_or_else(|| "fixtures/synthetic/phase1_synthetic_manifest.toml".to_string());
            let manifest_path = resolve_project_path(&root, &manifest);
            let report = validate_fixture_manifest(&root, &manifest_path)?;
            Ok(render_fixture_validation(&report, options.format))
        }
        [fixture_word, inspect_word, fixture_path]
            if fixture_word == "fixture" && inspect_word == "inspect" =>
        {
            let path = resolve_project_path(&root, fixture_path);
            let report = inspect_tja_file(&path)?;
            Ok(render_chart_inspection(&report, options.format))
        }
        [headless_word, autoplay_word]
            if headless_word == "headless" && autoplay_word == "autoplay" =>
        {
            let mode = HeadlessMode::parse(options.mode.as_deref().unwrap_or("perfect"))?;
            if let Some(chart) = options.chart.as_deref() {
                let chart_path = resolve_project_path(&root, chart);
                let report = autoplay_chart(&chart_path, mode)?;
                Ok(render_headless_autoplay(&report, options.format))
            } else {
                let manifest = options.manifest.clone().unwrap_or_else(|| {
                    "fixtures/synthetic/phase1_synthetic_manifest.toml".to_string()
                });
                let manifest_path = resolve_project_path(&root, &manifest);
                let report = autoplay_manifest(&root, &manifest_path, mode)?;
                Ok(render_headless_autoplay(&report, options.format))
            }
        }
        [timing_word, analyze_word] if timing_word == "timing" && analyze_word == "analyze" => {
            let threshold_ms = options.threshold_ms.unwrap_or(1.0);
            if let Some(input) = options.input.as_deref() {
                let input_path = resolve_project_path(&root, input);
                let text = read_file(&input_path)?;
                let timing_input = parse_headless_autoplay_json(&text)?;
                let report = analyze_headless_input(&timing_input, threshold_ms);
                Ok(render_timing_analysis(&report, options.format))
            } else {
                let manifest = options.manifest.clone().unwrap_or_else(|| {
                    "fixtures/synthetic/phase1_synthetic_manifest.toml".to_string()
                });
                let manifest_path = resolve_project_path(&root, &manifest);
                let headless = autoplay_manifest(&root, &manifest_path, HeadlessMode::Perfect)?;
                let timing_input =
                    timing_input_from_headless(&headless, "headless_autoplay_manifest");
                let report = analyze_headless_input(&timing_input, threshold_ms);
                Ok(render_timing_analysis(&report, options.format))
            }
        }
        [loop_word, failure_word, ingest_word, paths @ ..]
            if loop_word == "loop" && failure_word == "failure" && ingest_word == "ingest" =>
        {
            let reports = ingest_failures(&root, paths)?;
            Ok(render_failure_ingest(&reports, options.format))
        }
        [loop_word, failure_word, classify_word]
            if loop_word == "loop" && failure_word == "failure" && classify_word == "classify" =>
        {
            let Some(input) = options.input.as_deref().or(options.from_failure.as_deref()) else {
                return Err(CliError::Usage(
                    "loop failure classify requires --input PATH".to_string(),
                ));
            };
            let report_path = resolve_project_path(&root, input);
            let report = parse_failure_report_file(&root, &report_path)?;
            let classification = classify_failure_report(&report);
            Ok(render_failure_classification(
                &classification,
                options.format,
            ))
        }
        [loop_word, ticket_word, propose_word]
            if loop_word == "loop" && ticket_word == "ticket" && propose_word == "propose" =>
        {
            let Some(from_failure) = options.from_failure.as_deref() else {
                return Err(CliError::Usage(
                    "loop ticket propose requires --from-failure PATH".to_string(),
                ));
            };
            let report_path = resolve_project_path(&root, from_failure);
            let report = parse_failure_report_file(&root, &report_path)?;
            let proposed = propose_ticket_from_failure(&report);
            Ok(render_proposed_ticket(&proposed, options.format))
        }
        [loop_word, ticket_word, materialize_word]
            if loop_word == "loop"
                && ticket_word == "ticket"
                && materialize_word == "materialize" =>
        {
            let Some(from_failure) = options.from_failure.as_deref() else {
                return Err(CliError::Usage(
                    "loop ticket materialize requires --from-failure PATH".to_string(),
                ));
            };
            let report_path = resolve_project_path(&root, from_failure);
            let report = parse_failure_report_file(&root, &report_path)?;
            let materialized = materialize_ticket_from_failure(&root, &report)?;
            Ok(render_materialized_ticket(&materialized, options.format))
        }
        [loop_word, ticket_word, validate_word, ticket_path]
            if loop_word == "loop" && ticket_word == "ticket" && validate_word == "validate" =>
        {
            let path = resolve_project_path(&root, ticket_path);
            let validation = validate_repair_ticket(&root, &path)?;
            Ok(render_ticket_validation(&validation, options.format))
        }
        [loop_word, retry_word, check_word]
            if loop_word == "loop" && retry_word == "retry-budget" && check_word == "check" =>
        {
            let Some(ticket_id) = options.ticket.as_deref() else {
                return Err(CliError::Usage(
                    "loop retry-budget check requires --ticket TKT-xxxx".to_string(),
                ));
            };
            let report = check_retry_budget(&root, ticket_id)?;
            Ok(render_retry_budget_report(&report, options.format))
        }
        [qa_word, run_word] if qa_word == "qa" && run_word == "run" => {
            let report = run_qa(&root, &options)?;
            Ok(render_qa_run(&report, options.format))
        }
        [qa_word, compare_word] if qa_word == "qa" && compare_word == "compare" => {
            let report = compare_qa_reports(&root, &options)?;
            Ok(render_qa_compare(&report, options.format))
        }
        [qa_word, verdict_word] if qa_word == "qa" && verdict_word == "verdict" => {
            let Some(input) = options.input.as_deref() else {
                return Err(CliError::Usage(
                    "qa verdict requires --input PATH".to_string(),
                ));
            };
            let input_path = resolve_project_path(&root, input);
            let report = normalize_qa_verdict(&root, &input_path)?;
            Ok(render_qa_verdict(&report, options.format))
        }

        [phase1_word, feature_word, validate_word]
            if phase1_word == "phase1"
                && feature_word == "feature"
                && validate_word == "validate" =>
        {
            let report = validate_phase1_feature_manifest(&root, &options)?;
            Ok(render_phase1_feature_plan(&report, options.format))
        }
        [phase1_word, feature_word, plan_word]
            if phase1_word == "phase1" && feature_word == "feature" && plan_word == "plan" =>
        {
            let report = build_phase1_feature_plan(&root, &options)?;
            Ok(render_phase1_feature_plan(&report, options.format))
        }
        _ => Err(CliError::Usage(usage())),
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OutputFormat {
    Json,
    Markdown,
}

#[derive(Debug, Clone, PartialEq)]
struct CliOptions {
    words: Vec<String>,
    format: OutputFormat,
    dry_run: bool,
    manifest: Option<String>,
    chart: Option<String>,
    mode: Option<String>,
    input: Option<String>,
    threshold_ms: Option<f64>,
    from_failure: Option<String>,
    ticket: Option<String>,
    baseline: Option<String>,
    current: Option<String>,
}

fn parse_options(args: &[String]) -> CliResult<CliOptions> {
    let mut words = Vec::new();
    let mut format = OutputFormat::Markdown;
    let mut dry_run = false;
    let mut manifest = None;
    let mut chart = None;
    let mut mode = None;
    let mut input = None;
    let mut threshold_ms = None;
    let mut from_failure = None;
    let mut ticket = None;
    let mut baseline = None;
    let mut current = None;
    let mut index = 1;

    while index < args.len() {
        match args[index].as_str() {
            "--format" => {
                let Some(value) = args.get(index + 1) else {
                    return Err(CliError::Usage("--format requires a value".to_string()));
                };
                format = match value.as_str() {
                    "json" => OutputFormat::Json,
                    "markdown" | "md" => OutputFormat::Markdown,
                    other => {
                        return Err(CliError::Usage(format!(
                            "unsupported output format: {other}"
                        )))
                    }
                };
                index += 2;
            }
            "--dry-run" => {
                dry_run = true;
                index += 1;
            }
            "--manifest" => {
                let Some(value) = args.get(index + 1) else {
                    return Err(CliError::Usage("--manifest requires a value".to_string()));
                };
                manifest = Some(value.to_string());
                index += 2;
            }
            "--chart" => {
                let Some(value) = args.get(index + 1) else {
                    return Err(CliError::Usage("--chart requires a value".to_string()));
                };
                chart = Some(value.to_string());
                index += 2;
            }
            "--mode" => {
                let Some(value) = args.get(index + 1) else {
                    return Err(CliError::Usage("--mode requires a value".to_string()));
                };
                mode = Some(value.to_string());
                index += 2;
            }
            "--input" => {
                let Some(value) = args.get(index + 1) else {
                    return Err(CliError::Usage("--input requires a value".to_string()));
                };
                input = Some(value.to_string());
                index += 2;
            }
            "--threshold-ms" => {
                let Some(value) = args.get(index + 1) else {
                    return Err(CliError::Usage(
                        "--threshold-ms requires a value".to_string(),
                    ));
                };
                threshold_ms = Some(value.parse::<f64>().map_err(|_| {
                    CliError::Usage(format!("invalid --threshold-ms value: {value}"))
                })?);
                index += 2;
            }
            "--from-failure" => {
                let Some(value) = args.get(index + 1) else {
                    return Err(CliError::Usage(
                        "--from-failure requires a value".to_string(),
                    ));
                };
                from_failure = Some(value.to_string());
                index += 2;
            }
            "--ticket" => {
                let Some(value) = args.get(index + 1) else {
                    return Err(CliError::Usage("--ticket requires a value".to_string()));
                };
                ticket = Some(value.to_string());
                index += 2;
            }
            "--baseline" => {
                let Some(value) = args.get(index + 1) else {
                    return Err(CliError::Usage("--baseline requires a value".to_string()));
                };
                baseline = Some(value.to_string());
                index += 2;
            }
            "--current" => {
                let Some(value) = args.get(index + 1) else {
                    return Err(CliError::Usage("--current requires a value".to_string()));
                };
                current = Some(value.to_string());
                index += 2;
            }
            "--help" | "-h" => return Err(CliError::Usage(usage())),
            value => {
                words.push(value.to_string());
                index += 1;
            }
        }
    }

    Ok(CliOptions {
        words,
        format,
        dry_run,
        manifest,
        chart,
        mode,
        input,
        threshold_ms,
        from_failure,
        ticket,
        baseline,
        current,
    })
}

fn usage() -> String {
    "usage: taiko_cli <loop inspect tickets|loop inspect gates|loop next|loop run-once --mode plan|loop run-once --mode apply|loop gate GATE-0000 --dry-run|loop report status|fixture validate --manifest PATH|fixture inspect PATH|headless autoplay --chart PATH --mode perfect|headless autoplay --manifest PATH --mode perfect|timing analyze --input PATH|timing analyze --manifest PATH|loop failure ingest PATH...|loop failure classify --input PATH|loop ticket propose --from-failure PATH|loop ticket materialize --from-failure PATH|loop ticket validate PATH|loop retry-budget check --ticket TKT-xxxx|qa run --manifest PATH|qa compare --baseline DIR --current DIR|qa verdict --input PATH|phase1 feature validate --manifest PATH|phase1 feature plan --manifest PATH> [--threshold-ms N] [--format json]".to_string()
}

fn locate_project_root(start: PathBuf) -> CliResult<PathBuf> {
    let mut current = if start.is_file() {
        start.parent().unwrap_or(Path::new(".")).to_path_buf()
    } else {
        start
    };

    loop {
        if current.join("AGENTS.md").is_file() && current.join(".loop").is_dir() {
            return Ok(current);
        }
        if !current.pop() {
            return Err(CliError::MissingProjectRoot(
                env::current_dir().unwrap_or_else(|_| PathBuf::from(".")),
            ));
        }
    }
}

fn resolve_project_path(root: &Path, value: &str) -> PathBuf {
    let path = PathBuf::from(value);
    if path.is_absolute() {
        path
    } else {
        root.join(path)
    }
}

fn load_tickets(root: &Path) -> CliResult<Vec<Ticket>> {
    let dir = root.join(".loop/tickets");
    let files = list_markdown_files(&dir).map_err(|source| CliError::Io {
        path: dir.clone(),
        source,
    })?;
    let mut tickets = Vec::new();
    for file in files {
        let text = read_file(&file)?;
        tickets.push(parse_ticket(root, &file, &text));
    }
    tickets.sort_by(|left, right| left.id.cmp(&right.id));
    Ok(tickets)
}

fn load_gates(root: &Path) -> CliResult<Vec<Gate>> {
    let dir = root.join(".loop/gates");
    let files = list_markdown_files(&dir).map_err(|source| CliError::Io {
        path: dir.clone(),
        source,
    })?;
    let mut gates = Vec::new();
    for file in files {
        let text = read_file(&file)?;
        gates.push(parse_gate(root, &file, &text));
    }
    gates.sort_by(|left, right| left.id.cmp(&right.id));
    Ok(gates)
}

fn read_file(path: &Path) -> CliResult<String> {
    read_utf8(path).map_err(|source| CliError::Io {
        path: path.to_path_buf(),
        source,
    })
}

fn parse_ticket(root: &Path, file: &Path, text: &str) -> Ticket {
    let heading = text
        .lines()
        .find(|line| line.starts_with("# "))
        .unwrap_or("# UNKNOWN: Untitled");
    let id = extract_code(heading, "TKT-").unwrap_or_else(|| file_stem_id(file));
    let title = heading
        .split_once(':')
        .map(|(_, title)| title.trim().to_string())
        .unwrap_or_else(|| "Untitled".to_string());

    Ticket {
        id,
        title,
        status: field_value(text, "Status").unwrap_or_else(|| "Unknown".to_string()),
        owner_session: field_value(text, "Owner session").unwrap_or_default(),
        review_session: field_value(text, "Review session").unwrap_or_default(),
        dependencies: unique_codes(section(text, "Dependencies"), &["TKT-", "GATE-"]),
        required_checks: bullets_or_code(section(text, "Required checks")),
        evidence_requirements: bullets_or_code(section(text, "Evidence required")),
        path: relative(root, file),
    }
}

fn parse_gate(root: &Path, file: &Path, text: &str) -> Gate {
    let heading = text
        .lines()
        .find(|line| line.starts_with("# "))
        .unwrap_or("# UNKNOWN: Untitled");
    let id = extract_code(heading, "GATE-").unwrap_or_else(|| file_stem_id(file));
    let title = heading
        .split_once(':')
        .map(|(_, title)| title.trim().to_string())
        .unwrap_or_else(|| "Untitled".to_string());
    let output = section(text, "Output")
        .lines()
        .flat_map(extract_backticks)
        .find(|value| value.starts_with(".loop/") || value.starts_with("reports/"))
        .unwrap_or_default();

    Gate {
        id,
        title,
        status: field_value(text, "Status").unwrap_or_else(|| "Unknown".to_string()),
        owner: field_value(text, "Owner").unwrap_or_default(),
        reviewer: field_value(text, "Reviewer").unwrap_or_default(),
        scorecard_impact: unique_codes(section(text, "Autonomy scorecard impact"), &["A"]),
        required_inputs: required_inputs(section(text, "Required inputs")),
        pass_criteria: pass_criteria(section(text, "Pass criteria")),
        output_path: output,
        next_ticket_transition: section(text, "Next-ticket transition").trim().to_string(),
        path: relative(root, file),
    }
}

fn field_value(text: &str, name: &str) -> Option<String> {
    let prefix = format!("{name}:");
    text.lines().find_map(|line| {
        line.strip_prefix(&prefix)
            .map(|value| value.trim().to_string())
    })
}

fn section<'a>(text: &'a str, name: &str) -> &'a str {
    let mut search_start = 0;
    while let Some(relative_start) = text[search_start..].find("## ") {
        let start = search_start + relative_start;
        let heading_end = text[start..]
            .find('\n')
            .map(|offset| start + offset)
            .unwrap_or(text.len());
        let heading_line = text[start + 3..heading_end].trim();
        let normalized = heading_line
            .trim_start_matches(|ch: char| ch.is_ascii_digit() || ch == '.')
            .trim();
        if heading_line == name
            || normalized == name
            || normalized.starts_with(name)
            || heading_line.contains(name)
        {
            let body_start = if heading_end < text.len() {
                heading_end + 1
            } else {
                heading_end
            };
            let end = text[body_start..]
                .find("\n## ")
                .map(|offset| body_start + offset)
                .unwrap_or(text.len());
            return &text[body_start..end];
        }
        search_start = if heading_end < text.len() {
            heading_end + 1
        } else {
            heading_end
        };
    }
    ""
}

fn required_inputs(text: &str) -> Vec<String> {
    let mut values = Vec::new();
    for line in text.lines() {
        let line = line.trim();
        if let Some(value) = line.strip_prefix("- ") {
            let cleaned = trim_code(value);
            if !cleaned.is_empty() {
                values.push(cleaned);
            }
        }
    }
    values
}

fn pass_criteria(text: &str) -> Vec<String> {
    let mut values = Vec::new();
    for line in text.lines() {
        let line = line.trim();
        if line.starts_with('|')
            && !line.contains("---")
            && !line.contains("Check | Required result")
        {
            let columns: Vec<&str> = line.trim_matches('|').split('|').collect();
            if let Some(first) = columns.first() {
                let cleaned = trim_code(first.trim());
                if !cleaned.is_empty() {
                    values.push(cleaned);
                }
            }
        }
    }
    values
}

fn bullets_or_code(text: &str) -> Vec<String> {
    let mut values = Vec::new();
    for line in text.lines() {
        let trimmed = line.trim();
        if let Some(value) = trimmed.strip_prefix("- ") {
            values.push(trim_code(value));
        } else if trimmed.starts_with("cargo ") || trimmed.starts_with("taiko_cli ") {
            values.push(trim_code(trimmed));
        }
    }
    values.retain(|value| !value.is_empty());
    values
}

fn trim_code(value: &str) -> String {
    value
        .trim()
        .trim_matches('`')
        .trim_matches('.')
        .trim()
        .to_string()
}

fn extract_backticks(line: &str) -> Vec<String> {
    let mut values = Vec::new();
    let mut rest = line;
    while let Some(start) = rest.find('`') {
        rest = &rest[start + 1..];
        let Some(end) = rest.find('`') else {
            break;
        };
        values.push(rest[..end].to_string());
        rest = &rest[end + 1..];
    }
    values
}

fn unique_codes(text: &str, prefixes: &[&str]) -> Vec<String> {
    let mut values = Vec::new();
    for prefix in prefixes {
        let mut start = 0;
        while let Some(index) = text[start..].find(prefix) {
            let absolute = start + index;
            let code = read_code_at(text, absolute);
            if !code.is_empty() && !values.contains(&code) {
                values.push(code);
            }
            start = absolute + prefix.len();
        }
    }
    values
}

fn extract_code(text: &str, prefix: &str) -> Option<String> {
    text.find(prefix)
        .map(|index| read_code_at(text, index))
        .filter(|value| !value.is_empty())
}

fn read_code_at(text: &str, start: usize) -> String {
    text[start..]
        .chars()
        .take_while(|ch| ch.is_ascii_alphanumeric() || *ch == '-')
        .collect()
}

fn file_stem_id(file: &Path) -> String {
    file.file_stem()
        .and_then(|stem| stem.to_str())
        .unwrap_or("UNKNOWN")
        .to_string()
}

fn relative(root: &Path, file: &Path) -> String {
    file.strip_prefix(root)
        .unwrap_or(file)
        .to_string_lossy()
        .replace('\\', "/")
}

fn select_next_ticket(tickets: &[Ticket], gates: &[Gate], root: &Path) -> NextSelection {
    let mut ready: Vec<&Ticket> = tickets
        .iter()
        .filter(|ticket| ticket.status.eq_ignore_ascii_case("Ready"))
        .collect();
    ready.sort_by(|left, right| left.id.cmp(&right.id));

    for ticket in ready {
        let missing = missing_ticket_dependencies(ticket, tickets, gates, root);
        if missing.is_empty() {
            return NextSelection::Selected {
                ticket_id: ticket.id.clone(),
                reason: "lowest-numbered Ready ticket with satisfied dependencies".to_string(),
            };
        }
    }

    NextSelection::Block {
        reason: "no Ready ticket has satisfied dependencies".to_string(),
    }
}

fn missing_ticket_dependencies(
    ticket: &Ticket,
    tickets: &[Ticket],
    gates: &[Gate],
    root: &Path,
) -> Vec<String> {
    let ticket_status: BTreeMap<&str, &str> = tickets
        .iter()
        .map(|candidate| (candidate.id.as_str(), candidate.status.as_str()))
        .collect();
    let gate_ids: Vec<&str> = gates.iter().map(|gate| gate.id.as_str()).collect();
    let mut missing = Vec::new();

    for dependency in &ticket.dependencies {
        if dependency.starts_with("TKT-") {
            if ticket_status.get(dependency.as_str()) != Some(&"Done") {
                missing.push(format!("{dependency} not Done"));
            }
        } else if dependency.starts_with("GATE-") {
            if !gate_ids.contains(&dependency.as_str()) {
                missing.push(format!("{dependency} unknown"));
            } else if !gate_report_exists(root, dependency) {
                missing.push(format!("{dependency} report missing"));
            }
        }
    }

    missing
}

fn gate_report_exists(root: &Path, gate_id: &str) -> bool {
    root.join(format!(".loop/session_logs/{gate_id}-report.md"))
        .is_file()
}

#[derive(Debug, Clone, PartialEq, Eq)]
enum NextSelection {
    Selected { ticket_id: String, reason: String },
    Block { reason: String },
}

fn build_loop_run_once_plan(root: &Path, mode: &str) -> CliResult<LoopRunOncePlan> {
    if mode != "plan" && mode != "apply" {
        return Err(CliError::Usage(format!(
            "loop run-once --mode must be plan or apply, got: {mode}"
        )));
    }
    let tickets = load_tickets(root)?;
    let gates = load_gates(root)?;
    let status = build_status(root, &tickets, &gates);
    let selection = select_next_ticket(&tickets, &gates, root);

    let (selected_ticket, reason) = match selection {
        NextSelection::Selected { ticket_id, reason } => (Some(ticket_id), reason),
        NextSelection::Block { reason } => (None, reason),
    };

    let run_id = env::var("OPENTAIKO_LOOP_RUN_ID")
        .unwrap_or_else(|_| default_run_id(selected_ticket.as_deref(), mode));
    let report_dir = format!("reports/loop/{run_id}");
    let controller_report_json = format!("{report_dir}/controller_plan.json");
    let controller_report_markdown = format!("{report_dir}/controller_plan.md");
    let next_codex_prompt = format!("{report_dir}/next_codex_prompt.md");

    let branch = selected_ticket
        .as_deref()
        .and_then(|ticket_id| tickets.iter().find(|ticket| ticket.id == ticket_id))
        .map(branch_name_for_ticket);
    let implementation_worktree = selected_ticket
        .as_deref()
        .map(|ticket_id| format!("worktrees/impl/{ticket_id}"));
    let review_worktree = selected_ticket
        .as_deref()
        .map(|ticket_id| format!("worktrees/review/{ticket_id}"));
    let qa_worktree = selected_ticket
        .as_deref()
        .map(|ticket_id| format!("worktrees/qa/{ticket_id}"));
    let session_metadata_path = selected_ticket
        .as_deref()
        .map(|ticket_id| format!("reports/session_metadata/{ticket_id}.toml"));
    let required_commands = selected_ticket
        .as_deref()
        .and_then(|ticket_id| tickets.iter().find(|ticket| ticket.id == ticket_id))
        .map(|ticket| ticket.required_checks.clone())
        .unwrap_or_default();

    let (state, verdict, next_action) = if selected_ticket.is_some() {
        (
            "ready_ticket".to_string(),
            "plan".to_string(),
            "start_worker".to_string(),
        )
    } else if !status.open_failures.is_empty() {
        (
            "open_failures".to_string(),
            "block".to_string(),
            "classify_failure".to_string(),
        )
    } else {
        (
            "no_ready_ticket".to_string(),
            "block".to_string(),
            "wait_for_ready_ticket".to_string(),
        )
    };

    Ok(LoopRunOncePlan {
        run_id,
        mode: mode.to_string(),
        state,
        verdict,
        selected_ticket,
        next_action,
        reason,
        branch,
        implementation_worktree,
        review_worktree,
        qa_worktree,
        session_metadata_path,
        controller_report_json,
        controller_report_markdown,
        next_codex_prompt,
        required_commands,
        missing_gate_evidence: status.missing_gate_evidence,
        open_failures: status.open_failures,
        artifacts_written: Vec::new(),
    })
}

fn apply_loop_run_once_plan(root: &Path, mut plan: LoopRunOncePlan) -> CliResult<LoopRunOncePlan> {
    let report_dir = root.join(format!("reports/loop/{}", plan.run_id));
    fs::create_dir_all(&report_dir).map_err(|source| CliError::Io {
        path: report_dir.clone(),
        source,
    })?;

    let json_path = root.join(&plan.controller_report_json);
    let md_path = root.join(&plan.controller_report_markdown);
    let prompt_path = root.join(&plan.next_codex_prompt);
    let prompt = render_next_codex_prompt(&plan);
    let metadata_path = plan
        .session_metadata_path
        .as_ref()
        .map(|relative| root.join(relative));

    fs::write(
        &json_path,
        render_loop_run_once_plan(&plan, OutputFormat::Json),
    )
    .map_err(|source| CliError::Io {
        path: json_path.clone(),
        source,
    })?;
    fs::write(
        &md_path,
        render_loop_run_once_plan(&plan, OutputFormat::Markdown),
    )
    .map_err(|source| CliError::Io {
        path: md_path.clone(),
        source,
    })?;
    fs::write(&prompt_path, prompt).map_err(|source| CliError::Io {
        path: prompt_path.clone(),
        source,
    })?;

    if let Some(metadata_path) = metadata_path {
        if let Some(parent) = metadata_path.parent() {
            fs::create_dir_all(parent).map_err(|source| CliError::Io {
                path: parent.to_path_buf(),
                source,
            })?;
        }
        fs::write(&metadata_path, render_session_metadata(&plan)).map_err(|source| {
            CliError::Io {
                path: metadata_path.clone(),
                source,
            }
        })?;
    }

    plan.artifacts_written = vec![
        plan.controller_report_json.clone(),
        plan.controller_report_markdown.clone(),
        plan.next_codex_prompt.clone(),
    ];
    if let Some(path) = plan.session_metadata_path.clone() {
        plan.artifacts_written.push(path);
    }
    Ok(plan)
}

fn default_run_id(ticket_id: Option<&str>, mode: &str) -> String {
    let ticket = ticket_id.unwrap_or("NO-TICKET");
    let seconds = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_secs())
        .unwrap_or(0);
    format!("RUN-LOOP-{ticket}-{mode}-{seconds}")
}

fn branch_name_for_ticket(ticket: &Ticket) -> String {
    let prefix = match normalized_owner_session(&ticket.owner_session).as_str() {
        "control" => "loop",
        "spec" => "spec",
        "design" => "review",
        "test" => "test",
        "qa" => "qa",
        _ => "impl",
    };
    format!("{prefix}/{}-{}", ticket.id, slugify(&ticket.title))
}

fn normalized_owner_session(owner: &str) -> String {
    let lower = owner.to_ascii_lowercase();
    if lower.contains("control") {
        "control".to_string()
    } else if lower.contains("spec") {
        "spec".to_string()
    } else if lower.contains("design") || lower.contains("review") {
        "design".to_string()
    } else if lower.contains("test infra") || lower.contains("test infrastructure") {
        "test".to_string()
    } else if lower.contains("qa") || lower.contains("regression") {
        "qa".to_string()
    } else {
        "impl".to_string()
    }
}

fn slugify(value: &str) -> String {
    let mut slug = String::new();
    let mut previous_dash = false;
    for ch in value.chars() {
        if ch.is_ascii_alphanumeric() {
            slug.push(ch.to_ascii_lowercase());
            previous_dash = false;
        } else if !previous_dash {
            slug.push('-');
            previous_dash = true;
        }
    }
    let trimmed = slug.trim_matches('-').to_string();
    if trimmed.is_empty() {
        "ticket".to_string()
    } else {
        trimmed
    }
}

fn render_next_codex_prompt(plan: &LoopRunOncePlan) -> String {
    let ticket = plan.selected_ticket.as_deref().unwrap_or("none");
    let branch = plan.branch.as_deref().unwrap_or("none");
    let impl_worktree = plan.implementation_worktree.as_deref().unwrap_or("none");
    let review_worktree = plan.review_worktree.as_deref().unwrap_or("none");
    let qa_worktree = plan.qa_worktree.as_deref().unwrap_or("none");
    let metadata_path = plan
        .session_metadata_path
        .as_deref()
        .unwrap_or("reports/session_metadata/<ticket-id>.toml");
    format!(
        "# Next Codex Prompt for {ticket}\n\nRun ID: `{}`\nNext action: `{}`\nReason: {}\n\n## Required setup\n\n- Read `AGENTS.md` first.\n- Use branch `{branch}`.\n- Use implementation worktree `{impl_worktree}`.\n- Prepare review worktree `{review_worktree}` and QA worktree `{qa_worktree}` for later separated sessions.\n- Create or update session metadata at `{metadata_path}`.\n- Do not start Phase1 gameplay work unless the selected ticket is Ready.\n- Do not write QA verdict files from an Implementation Session.\n\n## Required commands\n\n{}\n\n## Controller artifacts\n\n- `{}`\n- `{}`\n- `{}`\n",
        plan.run_id,
        plan.next_action,
        plan.reason,
        markdown_bullets(&plan.required_commands),
        plan.controller_report_json,
        plan.controller_report_markdown,
        metadata_path,
    )
}

fn render_session_metadata(plan: &LoopRunOncePlan) -> String {
    let ticket = plan.selected_ticket.as_deref().unwrap_or("none");
    let branch = plan.branch.as_deref().unwrap_or("none");
    let impl_worktree = plan.implementation_worktree.as_deref().unwrap_or("none");
    let review_worktree = plan.review_worktree.as_deref().unwrap_or("none");
    let qa_worktree = plan.qa_worktree.as_deref().unwrap_or("none");
    format!(
        "# Step18 session metadata. Fill approval fields from separated sessions before merge.\n\nschema_version = 1\nrun_id = \"{}\"\nticket_id = \"{}\"\nimplementation_session_id = \"impl-{}\"\nreview_session_id = \"review-{}\"\nqa_session_id = \"qa-{}\"\nimplementation_branch = \"{}\"\nimplementation_worktree = \"{}\"\nreview_worktree = \"{}\"\nqa_worktree = \"{}\"\nqa_verdict_path = \"reports/qa/{}.verdict.json\"\npreflight_report_path = \"reports/preflight/{}/rust_preflight_report.json\"\nimplementation_may_write_code = true\nreview_may_write_code = false\nqa_may_write_code = false\ncontrol_may_merge = true\nnext_action = \"{}\"\n",
        plan.run_id,
        ticket,
        plan.run_id,
        plan.run_id,
        plan.run_id,
        branch,
        impl_worktree,
        review_worktree,
        qa_worktree,
        ticket,
        ticket,
        plan.next_action,
    )
}

fn markdown_bullets(values: &[String]) -> String {
    if values.is_empty() {
        "- No ticket-specific commands recorded. Read the ticket file and gate contract."
            .to_string()
    } else {
        values
            .iter()
            .map(|value| format!("- `{value}`"))
            .collect::<Vec<_>>()
            .join("\n")
    }
}

fn dry_run_gate(root: &Path, gate: &Gate) -> GateVerdict {
    let mut missing_inputs = Vec::new();
    let mut present_inputs = Vec::new();

    for input in &gate.required_inputs {
        let normalized = input.trim();
        if normalized.starts_with("Passed GATE-") {
            let gate_id = normalized.trim_start_matches("Passed ");
            if gate_report_exists(root, gate_id) {
                present_inputs.push(normalized.to_string());
            } else {
                missing_inputs.push(format!("{normalized} report"));
            }
        } else if looks_like_path(normalized) {
            if root.join(normalized).exists() {
                present_inputs.push(normalized.to_string());
            } else {
                missing_inputs.push(normalized.to_string());
            }
        } else {
            present_inputs.push(normalized.to_string());
        }
    }

    let verdict = if missing_inputs.is_empty() {
        "pass"
    } else {
        "block"
    }
    .to_string();
    GateVerdict {
        gate_id: gate.id.clone(),
        verdict,
        missing_inputs,
        present_inputs,
        pass_criteria_count: gate.pass_criteria.len(),
    }
}

fn looks_like_path(value: &str) -> bool {
    value.contains('/')
        || value.ends_with(".md")
        || value.ends_with(".toml")
        || value == "AGENTS.md"
        || value == "Cargo.toml"
}

fn build_status(root: &Path, tickets: &[Ticket], gates: &[Gate]) -> LoopStatus {
    let ready_tickets = tickets
        .iter()
        .filter(|ticket| ticket.status.eq_ignore_ascii_case("Ready"))
        .map(|ticket| ticket.id.clone())
        .collect::<Vec<_>>();
    let blocked_tickets = tickets
        .iter()
        .filter(|ticket| ticket.status.eq_ignore_ascii_case("Blocked"))
        .map(|ticket| ticket.id.clone())
        .collect::<Vec<_>>();
    let done_tickets = tickets
        .iter()
        .filter(|ticket| ticket.status.eq_ignore_ascii_case("Done"))
        .map(|ticket| ticket.id.clone())
        .collect::<Vec<_>>();
    let missing_gate_evidence = gates
        .iter()
        .filter(|gate| !gate_report_exists(root, &gate.id))
        .map(|gate| gate.id.clone())
        .collect::<Vec<_>>();
    let next_selected_ticket = match select_next_ticket(tickets, gates, root) {
        NextSelection::Selected { ticket_id, .. } => Some(ticket_id),
        NextSelection::Block { .. } => None,
    };
    let open_failures = list_open_failures(root);

    LoopStatus {
        autonomy_score_estimate: estimate_autonomy_score(root),
        ready_tickets,
        blocked_tickets,
        done_tickets,
        missing_gate_evidence,
        next_selected_ticket,
        open_failures,
    }
}

fn list_open_failures(root: &Path) -> Vec<String> {
    let dir = root.join("reports/failures");
    if !dir.is_dir() {
        return Vec::new();
    }
    let mut failures = Vec::new();
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.extension().and_then(|ext| ext.to_str()) == Some("md") {
                failures.push(relative(root, &path));
            }
        }
    }
    failures.sort();
    failures
}

fn estimate_autonomy_score(root: &Path) -> u32 {
    let mut score = 0;
    if root.join("AGENTS.md").is_file() && root.join("docs/61_worktree_policy.md").is_file() {
        score += 8;
    }
    if root.join("docs/05_autonomy_scorecard.md").is_file()
        && root.join("docs/06_gate_transition_rules.md").is_file()
        && root.join(".loop/tickets").is_dir()
        && root.join(".loop/gates").is_dir()
    {
        score += 11;
    }
    if root.join("Cargo.toml").is_file() && root.join("crates/taiko_cli").is_dir() {
        score += 10;
    }
    if root
        .join("fixtures/synthetic/phase1_synthetic_manifest.toml")
        .is_file()
        && root.join("crates/taiko_chart/src/lib.rs").is_file()
        && root.join("crates/taiko_runtime/src/lib.rs").is_file()
    {
        score += 12;
    }
    if root
        .join("docs/47_timing_log_analyzer_contract.md")
        .is_file()
        && root.join("crates/taiko_timing/src/lib.rs").is_file()
        && root
            .join("crates/taiko_cli/src/bin/timing_log_analyzer.rs")
            .is_file()
    {
        score += 12;
    } else if root.join("docs/43_timing_log_schema.md").is_file()
        && root.join("docs/44_timing_log_analyzer_spec.md").is_file()
    {
        score += 4;
    }
    if root
        .join("scripts/check_bootstrap_consistency.sh")
        .is_file()
        && root
            .join("scripts/check_timing_analyzer_static.py")
            .is_file()
    {
        score += 5;
    }
    if root.join("docs/07_failure_feedback_protocol.md").is_file()
        && root.join("templates/failure_report_template.md").is_file()
    {
        score += 5;
    }
    if root
        .join("docs/48_failure_feedback_loop_contract.md")
        .is_file()
        && root
            .join(".loop/gates/GATE-0070-failure-feedback-ready.md")
            .is_file()
        && root.join(".loop/tickets/TKT-0040.md").is_file()
    {
        score += 3;
    }
    if root
        .join("docs/49_qa_regression_gate_contract.md")
        .is_file()
        && root
            .join(".loop/gates/GATE-0080-qa-regression-ready.md")
            .is_file()
        && root.join(".github/workflows/phase1-loop.yml").is_file()
    {
        score += 8;
    }
    if root
        .join("docs/74_phase1_feature_loop_entry_contract.md")
        .is_file()
        && root
            .join(".loop/gates/GATE-0090-phase1-feature-loop-ready.md")
            .is_file()
        && root
            .join("operations/phase1_feature_ticket_manifest.toml")
            .is_file()
    {
        score += 7;
    }
    score
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FailureReport {
    pub failure_id: String,
    pub source_ticket_or_gate: String,
    pub category: String,
    pub reproduction_command: String,
    pub expected_class: String,
    pub actual_class: String,
    pub proposed_ticket_id: String,
    pub regression_command: String,
    pub duplicate_key: String,
    pub missing_fields: Vec<String>,
    pub path: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FailureIngestReport {
    pub verdict: String,
    pub report_count: usize,
    pub valid_count: usize,
    pub invalid_count: usize,
    pub duplicate_keys: Vec<String>,
    pub reports: Vec<FailureReport>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProposedTicket {
    pub ticket_id: String,
    pub title: String,
    pub status: String,
    pub category: String,
    pub source_failure_id: String,
    pub repair_scope: String,
    pub reproduction_command: String,
    pub regression_command: String,
    pub body: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FailureClassificationReport {
    pub verdict: String,
    pub route: String,
    pub repair_kind: String,
    pub source_failure_id: String,
    pub source_ticket_or_gate: String,
    pub category: String,
    pub materialized_ticket_id: String,
    pub original_ticket_should_remain: String,
    pub reason: String,
    pub missing_fields: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MaterializedTicketReport {
    pub verdict: String,
    pub route: String,
    pub repair_kind: String,
    pub ticket_id: String,
    pub path: String,
    pub source_failure_id: String,
    pub already_exists: bool,
    pub status: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RetryBudgetReport {
    pub verdict: String,
    pub ticket_id: String,
    pub max_repair_attempts_per_ticket: usize,
    pub max_block_attempts_per_gate: usize,
    pub max_same_failure_signature: usize,
    pub repair_attempts: usize,
    pub block_attempts: usize,
    pub same_failure_signature_count: usize,
    pub next_action: String,
    pub issues: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TicketValidationReport {
    pub verdict: String,
    pub ticket_id: String,
    pub missing_fields: Vec<String>,
    pub path: String,
}

fn ingest_failures(root: &Path, patterns: &[String]) -> CliResult<FailureIngestReport> {
    let mut paths = Vec::new();
    if patterns.is_empty() {
        let dir = root.join("reports/failures");
        if dir.is_dir() {
            paths.extend(markdown_files_recursive(&dir));
        }
    } else {
        for pattern in patterns {
            paths.extend(expand_report_pattern(root, pattern));
        }
    }
    paths.sort();
    paths.dedup();

    let mut reports = Vec::new();
    for path in paths {
        reports.push(parse_failure_report_file(root, &path)?);
    }

    let mut seen: BTreeMap<String, usize> = BTreeMap::new();
    for report in &reports {
        *seen.entry(report.duplicate_key.clone()).or_insert(0) += 1;
    }
    let duplicate_keys = seen
        .into_iter()
        .filter_map(|(key, count)| if count > 1 { Some(key) } else { None })
        .collect::<Vec<_>>();
    let invalid_count = reports
        .iter()
        .filter(|report| !report.missing_fields.is_empty())
        .count();
    let valid_count = reports.len().saturating_sub(invalid_count);
    let verdict = if invalid_count == 0 && duplicate_keys.is_empty() {
        "pass"
    } else {
        "reject"
    }
    .to_string();

    Ok(FailureIngestReport {
        verdict,
        report_count: reports.len(),
        valid_count,
        invalid_count,
        duplicate_keys,
        reports,
    })
}

fn expand_report_pattern(root: &Path, pattern: &str) -> Vec<PathBuf> {
    if pattern.contains('*') {
        let (dir_part, suffix) = match pattern.rsplit_once('/') {
            Some((dir, file_pattern)) => (dir, file_pattern.trim_start_matches('*')),
            None => (".", pattern.trim_start_matches('*')),
        };
        let dir = resolve_project_path(root, dir_part);
        if !dir.is_dir() {
            return Vec::new();
        }
        let mut paths = Vec::new();
        if let Ok(entries) = fs::read_dir(dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_file() {
                    let name = path
                        .file_name()
                        .and_then(|value| value.to_str())
                        .unwrap_or("");
                    if name.ends_with(suffix) {
                        paths.push(path);
                    }
                }
            }
        }
        paths
    } else {
        let path = resolve_project_path(root, pattern);
        if path.is_file() {
            vec![path]
        } else {
            Vec::new()
        }
    }
}

fn markdown_files_recursive(dir: &Path) -> Vec<PathBuf> {
    let mut paths = Vec::new();
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                paths.extend(markdown_files_recursive(&path));
            } else if path.extension().and_then(|ext| ext.to_str()) == Some("md") {
                paths.push(path);
            }
        }
    }
    paths
}

fn parse_failure_report_file(root: &Path, path: &Path) -> CliResult<FailureReport> {
    let text = read_file(path)?;
    let failure_id = table_value(&text, "Failure ID").unwrap_or_else(|| file_stem_id(path));
    let source_ticket_or_gate = table_value(&text, "Source ticket or gate").unwrap_or_default();
    let category = table_value(&text, "Category").unwrap_or_default();
    let reproduction_command = first_code_block(section(&text, "Failing command"))
        .or_else(|| table_value(&text, "Reproduction command"))
        .unwrap_or_default();
    let regression_command =
        first_code_block(section(&text, "Regression command required after repair"))
            .or_else(|| table_value(&text, "Regression command"))
            .unwrap_or_default();
    let (expected_class, actual_class) = expected_actual_classes(&text);
    let proposed_ticket_id =
        table_value(&text, "Proposed new repair ticket ID").unwrap_or_default();
    let duplicate_key = duplicate_key(
        &category,
        &reproduction_command,
        &expected_class,
        &actual_class,
    );

    let mut missing_fields = Vec::new();
    for (name, value) in [
        ("Failure ID", &failure_id),
        ("Source ticket or gate", &source_ticket_or_gate),
        ("Category", &category),
        ("Failing command", &reproduction_command),
        ("Expected class", &expected_class),
        ("Actual class", &actual_class),
        ("Proposed new repair ticket ID", &proposed_ticket_id),
        ("Regression command", &regression_command),
    ] {
        if value.trim().is_empty() {
            missing_fields.push(name.to_string());
        }
    }

    Ok(FailureReport {
        failure_id,
        source_ticket_or_gate,
        category,
        reproduction_command,
        expected_class,
        actual_class,
        proposed_ticket_id,
        regression_command,
        duplicate_key,
        missing_fields,
        path: relative(root, path),
    })
}

fn table_value(text: &str, field: &str) -> Option<String> {
    for line in text.lines() {
        let trimmed = line.trim();
        if !trimmed.starts_with('|') || trimmed.contains("---") {
            continue;
        }
        let columns = trimmed
            .trim_matches('|')
            .split('|')
            .map(|value| value.trim())
            .collect::<Vec<_>>();
        if columns.len() >= 2 && columns[0] == field {
            let value = trim_code(columns[1]);
            if !value.is_empty() {
                return Some(value);
            }
        }
    }
    None
}

fn first_code_block(text: &str) -> Option<String> {
    let mut in_code = false;
    let mut lines = Vec::new();
    for line in text.lines() {
        if line.trim_start().starts_with("```") {
            if in_code {
                break;
            }
            in_code = true;
            continue;
        }
        if in_code {
            lines.push(line);
        }
    }
    let value = lines.join("\n").trim().to_string();
    if value.is_empty() {
        None
    } else {
        Some(value)
    }
}

fn expected_actual_classes(text: &str) -> (String, String) {
    let mut expected_values = Vec::new();
    let mut actual_values = Vec::new();
    for line in section(text, "Expected vs actual").lines() {
        let trimmed = line.trim();
        if !trimmed.starts_with('|')
            || trimmed.contains("---")
            || trimmed.contains("Area | Expected | Actual")
        {
            continue;
        }
        let columns = trimmed
            .trim_matches('|')
            .split('|')
            .map(|value| trim_code(value.trim()))
            .collect::<Vec<_>>();
        if columns.len() >= 3 {
            if !columns[1].is_empty() {
                expected_values.push(format!("{}={}", columns[0], columns[1]));
            }
            if !columns[2].is_empty() {
                actual_values.push(format!("{}={}", columns[0], columns[2]));
            }
        }
    }
    (expected_values.join("; "), actual_values.join("; "))
}

fn duplicate_key(
    category: &str,
    reproduction_command: &str,
    expected_class: &str,
    actual_class: &str,
) -> String {
    format!(
        "{}|{}|{}|{}",
        category.trim(),
        reproduction_command.trim(),
        expected_class.trim(),
        actual_class.trim()
    )
}

fn classify_failure_report(report: &FailureReport) -> FailureClassificationReport {
    let (route, repair_kind, reason) = failure_route_for_category(
        &report.category,
        &report.reproduction_command,
        &report.missing_fields,
    );
    let ticket_id = materialized_ticket_id_for_failure(report, repair_kind);
    let original_ticket_should_remain = if route == "block" {
        "Blocked"
    } else {
        "Rejected"
    }
    .to_string();
    let verdict = if report.missing_fields.is_empty() {
        "pass"
    } else {
        "reject"
    }
    .to_string();
    FailureClassificationReport {
        verdict,
        route: route.to_string(),
        repair_kind: repair_kind.to_string(),
        source_failure_id: report.failure_id.clone(),
        source_ticket_or_gate: report.source_ticket_or_gate.clone(),
        category: report.category.clone(),
        materialized_ticket_id: ticket_id,
        original_ticket_should_remain,
        reason: reason.to_string(),
        missing_fields: report.missing_fields.clone(),
    }
}

fn failure_route_for_category<'a>(
    category: &str,
    reproduction_command: &str,
    missing_fields: &[String],
) -> (&'a str, &'a str, &'a str) {
    if !missing_fields.is_empty() {
        return (
            "block",
            "TOOL",
            "failure report is incomplete and cannot be routed safely",
        );
    }
    let lower_category = category.to_ascii_lowercase();
    let lower_command = reproduction_command.to_ascii_lowercase();
    if matches!(lower_category.as_str(), "spec_ambiguity") {
        (
            "block",
            "SPEC",
            "specification evidence must be repaired before implementation resumes",
        )
    } else if matches!(
        lower_category.as_str(),
        "opentaiko_evidence_gap"
            | "coverage_gap"
            | "fixture_manifest_error"
            | "fixture_file_missing"
    ) {
        ("block", "TOOL", "coverage, fixture, or evidence route must be repaired before feature implementation resumes")
    } else if matches!(
        lower_category.as_str(),
        "ci_tooling_error"
            | "fixture_cli_contract_error"
            | "headless_cli_contract_error"
            | "timing_cli_contract_error"
    ) && (lower_command.contains("command not found")
        || lower_command.contains("rustc")
        || lower_command.contains("cargo is required"))
    {
        ("block", "ENV", "environment or tool availability failed before implementation evidence could be judged")
    } else if matches!(lower_category.as_str(), "ci_tooling_error") {
        (
            "block",
            "TOOL",
            "CI or loop tooling failed before gameplay implementation could be judged",
        )
    } else {
        (
            "reject",
            "REPAIR",
            "implementation or contract behavior has concrete failing evidence",
        )
    }
}

fn materialized_ticket_id_for_failure(report: &FailureReport, repair_kind: &str) -> String {
    if report.proposed_ticket_id.starts_with("TKT-") {
        report.proposed_ticket_id.clone()
    } else {
        let suffix = report.failure_id.trim_start_matches("FF-");
        match repair_kind {
            "ENV" => format!("TKT-ENV-{suffix}"),
            "SPEC" => format!("TKT-SPEC-{suffix}"),
            "TOOL" => format!("TKT-TOOL-{suffix}"),
            _ => format!("TKT-REPAIR-{suffix}"),
        }
    }
}

fn materialize_ticket_from_failure(
    root: &Path,
    report: &FailureReport,
) -> CliResult<MaterializedTicketReport> {
    let classification = classify_failure_report(report);
    if classification.verdict != "pass" {
        return Err(CliError::Failure(format!(
            "cannot materialize ticket from invalid failure report {}: missing {}",
            report.path,
            classification.missing_fields.join(", ")
        )));
    }
    let ticket_id = classification.materialized_ticket_id.clone();
    let ticket_path = root.join(format!(".loop/tickets/{ticket_id}.md"));
    let already_exists = ticket_path.is_file();
    if !already_exists {
        let body = render_materialized_ticket_body(report, &classification);
        if let Some(parent) = ticket_path.parent() {
            fs::create_dir_all(parent).map_err(|source| CliError::Io {
                path: parent.to_path_buf(),
                source,
            })?;
        }
        fs::write(&ticket_path, body).map_err(|source| CliError::Io {
            path: ticket_path.clone(),
            source,
        })?;
    }
    Ok(MaterializedTicketReport {
        verdict: "pass".to_string(),
        route: classification.route,
        repair_kind: classification.repair_kind,
        ticket_id,
        path: relative(root, &ticket_path),
        source_failure_id: report.failure_id.clone(),
        already_exists,
        status: "Ready".to_string(),
    })
}

fn render_materialized_ticket_body(
    report: &FailureReport,
    classification: &FailureClassificationReport,
) -> String {
    let ticket_id = &classification.materialized_ticket_id;
    let title = materialized_ticket_title(report, classification);
    let owner_session = materialized_owner_session(&classification.repair_kind);
    let worktree = materialized_worktree(ticket_id, &classification.repair_kind);
    let source_state = &classification.original_ticket_should_remain;
    let repair_scope = repair_scope_for_category(&report.category);
    format!(
        "# {}: {}\n\nStatus: Ready\nOwner session: {}\nReview session: QA / Regression Session\nWorktree: `{}`\n\n## 1. Objective\n\nMaterialized by Step19 failure routing. Resolve failure `{}` classified as `{}` via `{}` route without broadening scope beyond the recorded evidence.\n\n## 2. Source failure\n\n- Failure report: `{}`\n- Source ticket or gate: `{}`\n- Source item remains: `{}`\n- Duplicate key: `{}`\n- Route: `{}`\n- Repair kind: `{}`\n- Route reason: {}\n\n## 3. Minimal repair scope\n\n{}\n\n## 4. Required reproduction command\n\n```bash\n{}\n```\n\n## 5. Required regression command\n\n```bash\n{}\n```\n\n## 6. Retry budget\n\n- Check budget before implementation: `taiko_cli loop retry-budget check --ticket {}`\n- Do not continue when retry budget verdict is `block`.\n\n## 7. Acceptance criteria\n\n- The reproduction command no longer fails.\n- The regression command returns a `pass` verdict.\n- `taiko_cli loop failure classify --input {}` keeps a stable route.\n- The original ticket or gate can be re-evaluated without manual judgement.\n",
        ticket_id,
        title,
        owner_session,
        worktree,
        report.failure_id,
        report.category,
        classification.route,
        report.path,
        report.source_ticket_or_gate,
        source_state,
        report.duplicate_key,
        classification.route,
        classification.repair_kind,
        classification.reason,
        repair_scope,
        report.reproduction_command,
        report.regression_command,
        ticket_id,
        report.path,
    )
}

fn materialized_ticket_title(
    report: &FailureReport,
    classification: &FailureClassificationReport,
) -> String {
    match classification.repair_kind.as_str() {
        "ENV" => format!("Environment blocker from {}", report.failure_id),
        "SPEC" => format!("Specification blocker from {}", report.failure_id),
        "TOOL" => format!("Tooling blocker from {}", report.failure_id),
        _ => format!("Repair {} from {}", report.category, report.failure_id),
    }
}

fn materialized_owner_session(repair_kind: &str) -> &'static str {
    match repair_kind {
        "ENV" | "TOOL" => "Test Infrastructure Session",
        "SPEC" => "Specification Extraction Session",
        _ => "Ticket Implementation Session",
    }
}

fn materialized_worktree(ticket_id: &str, repair_kind: &str) -> String {
    match repair_kind {
        "ENV" => format!("worktrees/env/{ticket_id}"),
        "SPEC" => format!("worktrees/spec/{ticket_id}"),
        "TOOL" => format!("worktrees/tool/{ticket_id}"),
        _ => format!("worktrees/repair/{ticket_id}"),
    }
}

fn check_retry_budget(root: &Path, ticket_id: &str) -> CliResult<RetryBudgetReport> {
    let limits = load_retry_budget_limits(root);
    let materialized_tickets = markdown_files_recursive(&root.join(".loop/tickets"));
    let failures = markdown_files_recursive(&root.join("reports/failures"));
    let mut repair_attempts = 0usize;
    let mut block_attempts = 0usize;
    let mut same_failure_signature_count = 0usize;
    let ticket_id_lower = ticket_id.to_ascii_lowercase();

    for path in materialized_tickets {
        let text = read_file(&path)?;
        let lower_text = text.to_ascii_lowercase();
        if lower_text.contains(&ticket_id_lower)
            || file_stem_id(&path).eq_ignore_ascii_case(ticket_id)
        {
            if lower_text.contains("route: `reject`")
                || lower_text.contains("tkt-repair")
                || lower_text.contains("worktrees/repair")
            {
                repair_attempts += 1;
            }
            if lower_text.contains("route: `block`")
                || lower_text.contains("tkt-env")
                || lower_text.contains("tkt-spec")
                || lower_text.contains("tkt-tool")
            {
                block_attempts += 1;
            }
        }
    }

    let mut duplicate_counts: BTreeMap<String, usize> = BTreeMap::new();
    for path in failures {
        let report = parse_failure_report_file(root, &path)?;
        if report.source_ticket_or_gate.eq_ignore_ascii_case(ticket_id)
            || report.proposed_ticket_id.eq_ignore_ascii_case(ticket_id)
        {
            *duplicate_counts.entry(report.duplicate_key).or_insert(0) += 1;
        }
    }
    if let Some(max_count) = duplicate_counts.values().max() {
        same_failure_signature_count = *max_count;
    }

    let mut issues = Vec::new();
    if repair_attempts > limits.max_repair_attempts_per_ticket {
        issues.push(format!(
            "repair attempts {} exceed max {}",
            repair_attempts, limits.max_repair_attempts_per_ticket
        ));
    }
    if block_attempts > limits.max_block_attempts_per_gate {
        issues.push(format!(
            "block attempts {} exceed max {}",
            block_attempts, limits.max_block_attempts_per_gate
        ));
    }
    if same_failure_signature_count > limits.max_same_failure_signature {
        issues.push(format!(
            "same failure signature count {} exceeds max {}",
            same_failure_signature_count, limits.max_same_failure_signature
        ));
    }
    let verdict = if issues.is_empty() { "pass" } else { "block" }.to_string();
    let next_action = if issues.is_empty() {
        "continue"
    } else {
        "stop_and_route_to_control"
    }
    .to_string();
    Ok(RetryBudgetReport {
        verdict,
        ticket_id: ticket_id.to_string(),
        max_repair_attempts_per_ticket: limits.max_repair_attempts_per_ticket,
        max_block_attempts_per_gate: limits.max_block_attempts_per_gate,
        max_same_failure_signature: limits.max_same_failure_signature,
        repair_attempts,
        block_attempts,
        same_failure_signature_count,
        next_action,
        issues,
    })
}

struct RetryBudgetLimits {
    max_repair_attempts_per_ticket: usize,
    max_block_attempts_per_gate: usize,
    max_same_failure_signature: usize,
}

fn load_retry_budget_limits(root: &Path) -> RetryBudgetLimits {
    let text = fs::read_to_string(root.join("operations/retry_budget.toml")).unwrap_or_default();
    RetryBudgetLimits {
        max_repair_attempts_per_ticket: toml_usize(&text, "max_repair_attempts_per_ticket")
            .unwrap_or(3),
        max_block_attempts_per_gate: toml_usize(&text, "max_block_attempts_per_gate").unwrap_or(2),
        max_same_failure_signature: toml_usize(&text, "max_same_failure_signature").unwrap_or(2),
    }
}

fn toml_usize(text: &str, key: &str) -> Option<usize> {
    let prefix = format!("{key} =");
    text.lines()
        .find_map(|line| {
            line.trim()
                .strip_prefix(&prefix)
                .map(|value| value.trim().trim_matches('"').to_string())
        })
        .and_then(|value| value.parse::<usize>().ok())
}

fn propose_ticket_from_failure(report: &FailureReport) -> ProposedTicket {
    let ticket_id = if report.proposed_ticket_id.trim().is_empty() {
        format!("TKT-REPAIR-{}", report.failure_id)
    } else {
        report.proposed_ticket_id.clone()
    };
    let title = format!("Repair {} from {}", report.category, report.failure_id);
    let repair_scope = repair_scope_for_category(&report.category).to_string();
    let body = format!(
        "# {}: {}\n\nStatus: Blocked\nOwner session: Ticket Implementation Session\nReview session: QA / Regression Session\nWorktree: `worktrees/repair/{}`\n\n## 1. Objective\n\nRepair failure `{}` classified as `{}` without broadening scope beyond the regression evidence.\n\n## 2. Source failure\n\n- Failure report: `{}`\n- Source ticket or gate: `{}`\n- Duplicate key: `{}`\n\n## 3. Minimal repair scope\n\n{}\n\n## 4. Required reproduction command\n\n```bash\n{}\n```\n\n## 5. Required regression command\n\n```bash\n{}\n```\n\n## 6. Acceptance criteria\n\n- The reproduction command no longer fails.\n- The regression command returns a `pass` verdict.\n- The original ticket or gate can be re-evaluated without manual judgement.\n",
        ticket_id,
        title,
        ticket_id,
        report.failure_id,
        report.category,
        report.path,
        report.source_ticket_or_gate,
        report.duplicate_key,
        repair_scope,
        report.reproduction_command,
        report.regression_command
    );
    ProposedTicket {
        ticket_id,
        title,
        status: "Blocked".to_string(),
        category: report.category.clone(),
        source_failure_id: report.failure_id.clone(),
        repair_scope,
        reproduction_command: report.reproduction_command.clone(),
        regression_command: report.regression_command.clone(),
        body,
    }
}

fn repair_scope_for_category(category: &str) -> &'static str {
    match category {
        "spec_ambiguity" => "Clarify conflicting acceptance criteria or contract text before implementation resumes.",
        "opentaiko_evidence_gap" => "Add source research and adoption decision evidence before implementation resumes.",
        "coverage_gap" => "Add or repair fixture, manifest, or coverage matrix evidence.",
        "parser_error" | "fixture_tja_structure_error" | "fixture_unknown_command" => "Repair TJA parsing or structural inspection only.",
        "chart_time_error" | "scroll_time_error" | "judgement_window_error" | "runtime_tick_error" => "Repair timing, scheduler, or runtime logic with analyzer evidence.",
        "autoplay_input_error" | "headless_autoplay_result_error" => "Repair headless autoplay input scheduling or result reporting.",
        "timing_cli_contract_error" | "headless_cli_contract_error" | "fixture_cli_contract_error" | "ci_tooling_error" => "Repair command contract, JSON output, or tooling surface.",
        "branch_route_error" => "Repair branch route parsing or branch condition evaluation.",
        "score_gauge_error" => "Repair score, combo, gauge, or clear-state calculation.",
        "audio_offset_error" => "Repair audio offset or latency evidence handling.",
        _ => "Repair the smallest module or document set required by the failure evidence.",
    }
}

fn validate_repair_ticket(root: &Path, path: &Path) -> CliResult<TicketValidationReport> {
    let text = read_file(path)?;
    let ticket = parse_ticket(root, path, &text);
    let mut missing_fields = Vec::new();
    for term in [
        "Source failure",
        "Required reproduction command",
        "Required regression command",
        "Acceptance criteria",
    ] {
        if !text.contains(term) {
            missing_fields.push(term.to_string());
        }
    }
    if ticket.id.is_empty() || ticket.id == "UNKNOWN" {
        missing_fields.push("ticket id".to_string());
    }
    if ticket.status.is_empty() {
        missing_fields.push("Status".to_string());
    }
    let verdict = if missing_fields.is_empty() {
        "pass"
    } else {
        "reject"
    }
    .to_string();
    Ok(TicketValidationReport {
        verdict,
        ticket_id: ticket.id,
        missing_fields,
        path: relative(root, path),
    })
}

#[derive(Debug, Clone, PartialEq)]
pub struct QaRunReport {
    pub verdict: String,
    pub manifest: String,
    pub threshold_ms: f64,
    pub fixture_verdict: String,
    pub headless_verdict: String,
    pub timing_verdict: String,
    pub failure_route_ready: bool,
    pub required_reports: Vec<String>,
    pub issues: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct QaCompareReport {
    pub verdict: String,
    pub baseline: String,
    pub current: String,
    pub compared_files: Vec<String>,
    pub missing_current: Vec<String>,
    pub missing_baseline: Vec<String>,
    pub differing_files: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct QaVerdictReport {
    pub verdict: String,
    pub source: String,
    pub source_verdict: String,
    pub ticket_id: String,
    pub run_id: String,
    pub qa_session_id: String,
    pub source_worktree: String,
    pub next_action: String,
    pub evidence_inputs: Vec<String>,
    pub failure_route: String,
    pub failure_report_required: bool,
    pub missing_evidence: Vec<String>,
    pub issues: Vec<String>,
}

fn run_qa(root: &Path, options: &CliOptions) -> CliResult<QaRunReport> {
    let manifest = options
        .manifest
        .clone()
        .unwrap_or_else(|| "fixtures/synthetic/phase1_synthetic_manifest.toml".to_string());
    let threshold_ms = options.threshold_ms.unwrap_or(1.0);
    let manifest_path = resolve_project_path(root, &manifest);
    if !manifest_path.is_file() {
        return Ok(QaRunReport {
            verdict: "block".to_string(),
            manifest,
            threshold_ms,
            fixture_verdict: "block".to_string(),
            headless_verdict: "block".to_string(),
            timing_verdict: "block".to_string(),
            failure_route_ready: failure_route_ready(root),
            required_reports: qa_required_reports(),
            issues: vec!["manifest path is missing".to_string()],
        });
    }

    let fixture = validate_fixture_manifest(root, &manifest_path)?;
    let headless = autoplay_manifest(root, &manifest_path, HeadlessMode::Perfect)?;
    let timing_input = timing_input_from_headless(&headless, "qa_run_headless_manifest");
    let timing = analyze_headless_input(&timing_input, threshold_ms);
    let failure_route_ready = failure_route_ready(root);
    let mut issues = Vec::new();

    if fixture.verdict != "pass" {
        issues.push(format!("fixture validation verdict is {}", fixture.verdict));
    }
    if headless.verdict != "pass" {
        issues.push(format!("headless autoplay verdict is {}", headless.verdict));
    }
    if timing.verdict != "pass" {
        issues.push(format!("timing analyzer verdict is {}", timing.verdict));
    }
    if !failure_route_ready {
        issues.push("failure feedback route is not ready".to_string());
    }

    let verdict = if !failure_route_ready {
        "block"
    } else if fixture.verdict == "pass" && headless.verdict == "pass" && timing.verdict == "pass" {
        "pass"
    } else {
        "reject"
    };

    Ok(QaRunReport {
        verdict: verdict.to_string(),
        manifest,
        threshold_ms,
        fixture_verdict: fixture.verdict,
        headless_verdict: headless.verdict,
        timing_verdict: timing.verdict,
        failure_route_ready,
        required_reports: qa_required_reports(),
        issues,
    })
}

fn failure_route_ready(root: &Path) -> bool {
    root.join("docs/48_failure_feedback_loop_contract.md")
        .is_file()
        && root.join("templates/failure_report_template.md").is_file()
        && root
            .join(".loop/gates/GATE-0070-failure-feedback-ready.md")
            .is_file()
        && root.join(".loop/tickets/TKT-0040.md").is_file()
}

fn qa_required_reports() -> Vec<String> {
    vec![
        "reports/qa/phase1_loop.qa.json".to_string(),
        "reports/qa/phase1_loop.compare.json".to_string(),
        "reports/qa/phase1_loop.verdict.json".to_string(),
    ]
}

fn compare_qa_reports(root: &Path, options: &CliOptions) -> CliResult<QaCompareReport> {
    let baseline = options
        .baseline
        .clone()
        .unwrap_or_else(|| "reports/baseline".to_string());
    let current = options
        .current
        .clone()
        .unwrap_or_else(|| "reports/current".to_string());
    let baseline_path = resolve_project_path(root, &baseline);
    let current_path = resolve_project_path(root, &current);

    if !baseline_path.is_dir() || !current_path.is_dir() {
        let mut missing_current = Vec::new();
        let mut missing_baseline = Vec::new();
        if !current_path.is_dir() {
            missing_current.push(current.clone());
        }
        if !baseline_path.is_dir() {
            missing_baseline.push(baseline.clone());
        }
        return Ok(QaCompareReport {
            verdict: "block".to_string(),
            baseline,
            current,
            compared_files: Vec::new(),
            missing_current,
            missing_baseline,
            differing_files: Vec::new(),
        });
    }

    let baseline_files = report_files(&baseline_path);
    let current_files = report_files(&current_path);
    let mut compared_files = Vec::new();
    let mut missing_current = Vec::new();
    let mut missing_baseline = Vec::new();
    let mut differing_files = Vec::new();

    for relative_path in &baseline_files {
        let baseline_file = baseline_path.join(relative_path);
        let current_file = current_path.join(relative_path);
        if !current_file.is_file() {
            missing_current.push(relative_path.to_string_lossy().to_string());
            continue;
        }
        compared_files.push(relative_path.to_string_lossy().to_string());
        if read_file_lossy(&baseline_file) != read_file_lossy(&current_file) {
            differing_files.push(relative_path.to_string_lossy().to_string());
        }
    }

    for relative_path in &current_files {
        if !baseline_path.join(relative_path).is_file() {
            missing_baseline.push(relative_path.to_string_lossy().to_string());
        }
    }

    let verdict = if missing_current.is_empty()
        && missing_baseline.is_empty()
        && differing_files.is_empty()
    {
        "pass"
    } else {
        "reject"
    };

    Ok(QaCompareReport {
        verdict: verdict.to_string(),
        baseline,
        current,
        compared_files,
        missing_current,
        missing_baseline,
        differing_files,
    })
}

fn normalize_qa_verdict(root: &Path, input_path: &Path) -> CliResult<QaVerdictReport> {
    let source = relative(root, input_path);
    if !input_path.is_file() {
        return Ok(QaVerdictReport {
            verdict: "block".to_string(),
            source,
            source_verdict: "missing".to_string(),
            ticket_id: String::new(),
            run_id: String::new(),
            qa_session_id: String::new(),
            source_worktree: String::new(),
            next_action: "produce QA input report before gate evaluation".to_string(),
            evidence_inputs: Vec::new(),
            failure_route: "{}".to_string(),
            failure_report_required: false,
            missing_evidence: vec!["qa input report is missing".to_string()],
            issues: vec!["qa input report is missing".to_string()],
        });
    }
    let text = read_file(input_path)?;
    let source_verdict =
        json_string_field(&text, "verdict").unwrap_or_else(|| "unknown".to_string());
    let ticket_id = json_string_field(&text, "ticket_id").unwrap_or_default();
    let run_id = json_string_field(&text, "run_id").unwrap_or_default();
    let qa_session_id = json_string_field(&text, "qa_session_id")
        .or_else(|| json_string_field(&text, "session_id"))
        .unwrap_or_default();
    let source_worktree = json_string_field(&text, "source_worktree").unwrap_or_default();
    let failure_route =
        json_object_fragment(&text, "failure_route").unwrap_or_else(|| "{}".to_string());
    let evidence_inputs = json_string_array_field(&text, "evidence_inputs");
    let missing_evidence = json_string_array_field(&text, "missing_evidence");
    let mut issues = Vec::new();
    for (field, value) in [
        ("ticket_id", &ticket_id),
        ("run_id", &run_id),
        ("qa_session_id", &qa_session_id),
        ("source_worktree", &source_worktree),
    ] {
        if value.is_empty() {
            issues.push(format!("missing required QA verdict field: {field}"));
        }
    }
    if evidence_inputs.is_empty() {
        issues.push("missing required QA verdict field: evidence_inputs".to_string());
    }
    if !text.contains("\"failure_route\"") {
        issues.push("missing required QA verdict field: failure_route".to_string());
    }

    let (mut verdict, next_action, failure_report_required) = match source_verdict.as_str() {
        "pass" => ("pass", "advance to next eligible ticket", false),
        "reject" => (
            "reject",
            "create or update failure report and materialized repair ticket",
            true,
        ),
        "block" => (
            "block",
            "produce missing evidence and route blocker ticket",
            false,
        ),
        _ => ("block", "repair QA report or CLI contract", false),
    };
    if source_verdict == "reject" {
        for field in [
            "classification_path",
            "materialization_path",
            "repair_ticket_id",
        ] {
            if !failure_route.contains(&format!("\"{field}\"")) {
                issues.push(format!("reject QA verdict requires failure_route.{field}"));
            }
        }
    }
    if source_verdict == "block" {
        if missing_evidence.is_empty() {
            issues.push("block QA verdict requires missing_evidence".to_string());
        }
        for field in ["blocker_ticket_id", "blocker_route"] {
            if !failure_route.contains(&format!("\"{field}\"")) {
                issues.push(format!("block QA verdict requires failure_route.{field}"));
            }
        }
    }
    if !issues.is_empty() && verdict == "pass" {
        verdict = "block";
    }
    Ok(QaVerdictReport {
        verdict: verdict.to_string(),
        source,
        source_verdict,
        ticket_id,
        run_id,
        qa_session_id,
        source_worktree,
        next_action: next_action.to_string(),
        evidence_inputs,
        failure_route,
        failure_report_required,
        missing_evidence,
        issues,
    })
}

fn report_files(root: &Path) -> Vec<PathBuf> {
    let mut paths = Vec::new();
    collect_report_files(root, root, &mut paths);
    paths.sort();
    paths
}

fn collect_report_files(root: &Path, current: &Path, paths: &mut Vec<PathBuf>) {
    if let Ok(entries) = fs::read_dir(current) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                collect_report_files(root, &path, paths);
            } else if path.is_file() {
                if let Ok(relative) = path.strip_prefix(root) {
                    paths.push(relative.to_path_buf());
                }
            }
        }
    }
}

fn read_file_lossy(path: &Path) -> String {
    fs::read_to_string(path).unwrap_or_default()
}

fn json_string_field(text: &str, field: &str) -> Option<String> {
    let needle = format!("\"{field}\"");
    let start = text.find(&needle)?;
    let rest = &text[start + needle.len()..];
    let colon = rest.find(':')?;
    let after_colon = rest[colon + 1..].trim_start();
    let value = after_colon.strip_prefix('"')?;
    let end = value.find('"')?;
    Some(value[..end].to_string())
}

fn json_string_array_field(text: &str, field: &str) -> Vec<String> {
    let needle = format!("\"{field}\"");
    let Some(start) = text.find(&needle) else {
        return Vec::new();
    };
    let rest = &text[start + needle.len()..];
    let Some(colon) = rest.find(':') else {
        return Vec::new();
    };
    let after_colon = rest[colon + 1..].trim_start();
    let Some(array) = after_colon.strip_prefix('[') else {
        return Vec::new();
    };
    let Some(end) = array.find(']') else {
        return Vec::new();
    };
    array[..end]
        .split(',')
        .filter_map(|item| {
            let item = item.trim();
            let value = item.strip_prefix('"')?.strip_suffix('"')?;
            Some(value.to_string())
        })
        .collect()
}

fn json_object_fragment(text: &str, field: &str) -> Option<String> {
    let needle = format!("\"{field}\"");
    let start = text.find(&needle)?;
    let rest = &text[start + needle.len()..];
    let colon = rest.find(':')?;
    let after_colon = rest[colon + 1..].trim_start();
    let object = after_colon.strip_prefix('{')?;
    let end = object.find('}')?;
    Some(format!("{{{}}}", &object[..end]))
}

fn render_qa_run(report: &QaRunReport, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"verdict\":\"{}\",\"manifest\":\"{}\",\"threshold_ms\":{},\"fixture_verdict\":\"{}\",\"headless_verdict\":\"{}\",\"timing_verdict\":\"{}\",\"failure_route_ready\":{},\"required_reports\":{},\"issues\":{}}}",
            escape_json(&report.verdict),
            escape_json(&report.manifest),
            report.threshold_ms,
            escape_json(&report.fixture_verdict),
            escape_json(&report.headless_verdict),
            escape_json(&report.timing_verdict),
            report.failure_route_ready,
            string_array_json(&report.required_reports),
            string_array_json(&report.issues)
        ),
        OutputFormat::Markdown => format!(
            "verdict: {}\nmanifest: {}\nthreshold_ms: {}\nfixture: {}\nheadless: {}\ntiming: {}\nfailure route ready: {}\nissues: {}",
            report.verdict,
            report.manifest,
            report.threshold_ms,
            report.fixture_verdict,
            report.headless_verdict,
            report.timing_verdict,
            report.failure_route_ready,
            report.issues.join(", ")
        ),
    }
}

fn render_qa_compare(report: &QaCompareReport, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"verdict\":\"{}\",\"baseline\":\"{}\",\"current\":\"{}\",\"compared_files\":{},\"missing_current\":{},\"missing_baseline\":{},\"differing_files\":{}}}",
            escape_json(&report.verdict),
            escape_json(&report.baseline),
            escape_json(&report.current),
            string_array_json(&report.compared_files),
            string_array_json(&report.missing_current),
            string_array_json(&report.missing_baseline),
            string_array_json(&report.differing_files)
        ),
        OutputFormat::Markdown => format!(
            "verdict: {}\nbaseline: {}\ncurrent: {}\ncompared: {}\nmissing current: {}\nmissing baseline: {}\ndiffering: {}",
            report.verdict,
            report.baseline,
            report.current,
            report.compared_files.join(", "),
            report.missing_current.join(", "),
            report.missing_baseline.join(", "),
            report.differing_files.join(", ")
        ),
    }
}

fn render_qa_verdict(report: &QaVerdictReport, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"verdict\":\"{}\",\"source\":\"{}\",\"source_verdict\":\"{}\",\"ticket_id\":\"{}\",\"run_id\":\"{}\",\"qa_session_id\":\"{}\",\"source_worktree\":\"{}\",\"next_action\":\"{}\",\"evidence_inputs\":{},\"failure_route\":{},\"failure_report_required\":{},\"missing_evidence\":{},\"issues\":{}}}",
            escape_json(&report.verdict),
            escape_json(&report.source),
            escape_json(&report.source_verdict),
            escape_json(&report.ticket_id),
            escape_json(&report.run_id),
            escape_json(&report.qa_session_id),
            escape_json(&report.source_worktree),
            escape_json(&report.next_action),
            string_array_json(&report.evidence_inputs),
            report.failure_route,
            report.failure_report_required,
            string_array_json(&report.missing_evidence),
            string_array_json(&report.issues)
        ),
        OutputFormat::Markdown => format!(
            "verdict: {}\nsource: {}\nsource verdict: {}\nticket: {}\nrun: {}\nqa session: {}\nsource worktree: {}\nnext action: {}\nevidence inputs: {}\nfailure route: {}\nfailure report required: {}\nmissing evidence: {}\nissues: {}",
            report.verdict,
            report.source,
            report.source_verdict,
            report.ticket_id,
            report.run_id,
            report.qa_session_id,
            report.source_worktree,
            report.next_action,
            report.evidence_inputs.join(", "),
            report.failure_route,
            report.failure_report_required,
            report.missing_evidence.join(", "),
            report.issues.join(", ")
        ),
    }
}

fn render_failure_ingest(report: &FailureIngestReport, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => {
            let items = report
                .reports
                .iter()
                .map(failure_report_json)
                .collect::<Vec<_>>()
                .join(",");
            format!("{{\"verdict\":\"{}\",\"report_count\":{},\"valid_count\":{},\"invalid_count\":{},\"duplicate_keys\":{},\"reports\":[{}]}}", escape_json(&report.verdict), report.report_count, report.valid_count, report.invalid_count, string_array_json(&report.duplicate_keys), items)
        }
        OutputFormat::Markdown => format!(
            "verdict: {}\nreports: {}\nvalid: {}\ninvalid: {}\nduplicates: {}",
            report.verdict,
            report.report_count,
            report.valid_count,
            report.invalid_count,
            report.duplicate_keys.join(", ")
        ),
    }
}

fn render_proposed_ticket(ticket: &ProposedTicket, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!("{{\"ticket_id\":\"{}\",\"title\":\"{}\",\"status\":\"{}\",\"category\":\"{}\",\"source_failure_id\":\"{}\",\"repair_scope\":\"{}\",\"reproduction_command\":\"{}\",\"regression_command\":\"{}\",\"body\":\"{}\"}}", escape_json(&ticket.ticket_id), escape_json(&ticket.title), escape_json(&ticket.status), escape_json(&ticket.category), escape_json(&ticket.source_failure_id), escape_json(&ticket.repair_scope), escape_json(&ticket.reproduction_command), escape_json(&ticket.regression_command), escape_json(&ticket.body)),
        OutputFormat::Markdown => ticket.body.clone(),
    }
}

fn render_failure_classification(
    report: &FailureClassificationReport,
    format: OutputFormat,
) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"verdict\":\"{}\",\"route\":\"{}\",\"repair_kind\":\"{}\",\"source_failure_id\":\"{}\",\"source_ticket_or_gate\":\"{}\",\"category\":\"{}\",\"materialized_ticket_id\":\"{}\",\"original_ticket_should_remain\":\"{}\",\"reason\":\"{}\",\"missing_fields\":{}}}",
            escape_json(&report.verdict),
            escape_json(&report.route),
            escape_json(&report.repair_kind),
            escape_json(&report.source_failure_id),
            escape_json(&report.source_ticket_or_gate),
            escape_json(&report.category),
            escape_json(&report.materialized_ticket_id),
            escape_json(&report.original_ticket_should_remain),
            escape_json(&report.reason),
            string_array_json(&report.missing_fields)
        ),
        OutputFormat::Markdown => format!(
            "verdict: {}\nroute: {}\nrepair_kind: {}\nsource_failure_id: {}\nsource_ticket_or_gate: {}\ncategory: {}\nmaterialized_ticket_id: {}\noriginal_ticket_should_remain: {}\nreason: {}\nmissing_fields: {}",
            report.verdict,
            report.route,
            report.repair_kind,
            report.source_failure_id,
            report.source_ticket_or_gate,
            report.category,
            report.materialized_ticket_id,
            report.original_ticket_should_remain,
            report.reason,
            report.missing_fields.join(", ")
        ),
    }
}

fn render_materialized_ticket(report: &MaterializedTicketReport, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"verdict\":\"{}\",\"route\":\"{}\",\"repair_kind\":\"{}\",\"ticket_id\":\"{}\",\"path\":\"{}\",\"source_failure_id\":\"{}\",\"already_exists\":{},\"status\":\"{}\"}}",
            escape_json(&report.verdict),
            escape_json(&report.route),
            escape_json(&report.repair_kind),
            escape_json(&report.ticket_id),
            escape_json(&report.path),
            escape_json(&report.source_failure_id),
            report.already_exists,
            escape_json(&report.status)
        ),
        OutputFormat::Markdown => format!(
            "verdict: {}\nroute: {}\nrepair_kind: {}\nticket: {}\npath: {}\nsource_failure_id: {}\nalready_exists: {}\nstatus: {}",
            report.verdict,
            report.route,
            report.repair_kind,
            report.ticket_id,
            report.path,
            report.source_failure_id,
            report.already_exists,
            report.status
        ),
    }
}

fn render_retry_budget_report(report: &RetryBudgetReport, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"verdict\":\"{}\",\"ticket_id\":\"{}\",\"max_repair_attempts_per_ticket\":{},\"max_block_attempts_per_gate\":{},\"max_same_failure_signature\":{},\"repair_attempts\":{},\"block_attempts\":{},\"same_failure_signature_count\":{},\"next_action\":\"{}\",\"issues\":{}}}",
            escape_json(&report.verdict),
            escape_json(&report.ticket_id),
            report.max_repair_attempts_per_ticket,
            report.max_block_attempts_per_gate,
            report.max_same_failure_signature,
            report.repair_attempts,
            report.block_attempts,
            report.same_failure_signature_count,
            escape_json(&report.next_action),
            string_array_json(&report.issues)
        ),
        OutputFormat::Markdown => format!(
            "verdict: {}\nticket: {}\nrepair_attempts: {}/{}\nblock_attempts: {}/{}\nsame_failure_signature_count: {}/{}\nnext_action: {}\nissues: {}",
            report.verdict,
            report.ticket_id,
            report.repair_attempts,
            report.max_repair_attempts_per_ticket,
            report.block_attempts,
            report.max_block_attempts_per_gate,
            report.same_failure_signature_count,
            report.max_same_failure_signature,
            report.next_action,
            report.issues.join(", ")
        ),
    }
}

fn render_ticket_validation(report: &TicketValidationReport, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"verdict\":\"{}\",\"ticket_id\":\"{}\",\"missing_fields\":{},\"path\":\"{}\"}}",
            escape_json(&report.verdict),
            escape_json(&report.ticket_id),
            string_array_json(&report.missing_fields),
            escape_json(&report.path)
        ),
        OutputFormat::Markdown => format!(
            "ticket: {}\nverdict: {}\nmissing fields: {}\npath: {}",
            report.ticket_id,
            report.verdict,
            report.missing_fields.join(", "),
            report.path
        ),
    }
}

fn failure_report_json(report: &FailureReport) -> String {
    format!("{{\"failure_id\":\"{}\",\"source_ticket_or_gate\":\"{}\",\"category\":\"{}\",\"reproduction_command\":\"{}\",\"expected_class\":\"{}\",\"actual_class\":\"{}\",\"proposed_ticket_id\":\"{}\",\"regression_command\":\"{}\",\"duplicate_key\":\"{}\",\"missing_fields\":{},\"path\":\"{}\"}}", escape_json(&report.failure_id), escape_json(&report.source_ticket_or_gate), escape_json(&report.category), escape_json(&report.reproduction_command), escape_json(&report.expected_class), escape_json(&report.actual_class), escape_json(&report.proposed_ticket_id), escape_json(&report.regression_command), escape_json(&report.duplicate_key), string_array_json(&report.missing_fields), escape_json(&report.path))
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Phase1FeatureTicket {
    pub ticket_id: String,
    pub title: String,
    pub stage: String,
    pub category: String,
    pub depends_on: Vec<String>,
    pub required_commands: Vec<String>,
    pub acceptance_docs: Vec<String>,
    pub qa_required: bool,
    pub failure_route_required: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Phase1FeaturePlanReport {
    pub verdict: String,
    pub manifest: String,
    pub feature_ticket_count: usize,
    pub first_feature_ticket: Option<String>,
    pub next_ticket: Option<String>,
    pub blocked_count: usize,
    pub qa_required_count: usize,
    pub failure_route_required_count: usize,
    pub issues: Vec<String>,
}

fn validate_phase1_feature_manifest(
    root: &Path,
    options: &CliOptions,
) -> CliResult<Phase1FeaturePlanReport> {
    let (manifest_display, tickets, issues) = load_phase1_feature_manifest(root, options)?;
    phase1_feature_report(root, manifest_display, tickets, issues, false)
}

fn build_phase1_feature_plan(
    root: &Path,
    options: &CliOptions,
) -> CliResult<Phase1FeaturePlanReport> {
    let (manifest_display, tickets, issues) = load_phase1_feature_manifest(root, options)?;
    phase1_feature_report(root, manifest_display, tickets, issues, true)
}

fn load_phase1_feature_manifest(
    root: &Path,
    options: &CliOptions,
) -> CliResult<(String, Vec<Phase1FeatureTicket>, Vec<String>)> {
    let manifest = options
        .manifest
        .clone()
        .unwrap_or_else(|| "operations/phase1_feature_ticket_manifest.toml".to_string());
    let manifest_path = resolve_project_path(root, &manifest);
    let text = read_file(&manifest_path)?;
    let tickets = parse_phase1_feature_manifest(&text);
    let mut issues = Vec::new();
    if tickets.is_empty() {
        issues.push("manifest contains no [[tickets]] entries".to_string());
    }
    Ok((relative(root, &manifest_path), tickets, issues))
}

fn parse_phase1_feature_manifest(text: &str) -> Vec<Phase1FeatureTicket> {
    let mut entries: Vec<BTreeMap<String, String>> = Vec::new();
    let mut current: Option<BTreeMap<String, String>> = None;
    for raw_line in text.lines() {
        let line = raw_line.split('#').next().unwrap_or("").trim();
        if line.is_empty() {
            continue;
        }
        if line == "[[tickets]]" {
            if let Some(entry) = current.take() {
                entries.push(entry);
            }
            current = Some(BTreeMap::new());
            continue;
        }
        let Some((key, value)) = line.split_once('=') else {
            continue;
        };
        if let Some(entry) = current.as_mut() {
            entry.insert(key.trim().to_string(), value.trim().to_string());
        }
    }
    if let Some(entry) = current.take() {
        entries.push(entry);
    }
    entries
        .into_iter()
        .map(|entry| Phase1FeatureTicket {
            ticket_id: toml_string(entry.get("ticket_id")).unwrap_or_default(),
            title: toml_string(entry.get("title")).unwrap_or_default(),
            stage: toml_string(entry.get("stage")).unwrap_or_default(),
            category: toml_string(entry.get("category")).unwrap_or_default(),
            depends_on: toml_array(entry.get("depends_on")),
            required_commands: toml_array(entry.get("required_commands")),
            acceptance_docs: toml_array(entry.get("acceptance_docs")),
            qa_required: toml_bool(entry.get("qa_required")),
            failure_route_required: toml_bool(entry.get("failure_route_required")),
        })
        .collect()
}

fn phase1_feature_report(
    root: &Path,
    manifest: String,
    tickets: Vec<Phase1FeatureTicket>,
    mut issues: Vec<String>,
    include_plan: bool,
) -> CliResult<Phase1FeaturePlanReport> {
    let loaded_tickets = load_tickets(root)?;
    let loaded_gates = load_gates(root)?;
    let ticket_status: BTreeMap<&str, &str> = loaded_tickets
        .iter()
        .map(|ticket| (ticket.id.as_str(), ticket.status.as_str()))
        .collect();
    let gate_ids = loaded_gates
        .iter()
        .map(|gate| gate.id.as_str())
        .collect::<Vec<_>>();

    let mut next_ticket = None;
    let mut blocked_count = 0usize;
    let mut qa_required_count = 0usize;
    let mut failure_route_required_count = 0usize;

    for ticket in &tickets {
        if !root
            .join(format!(".loop/tickets/{}.md", ticket.ticket_id))
            .is_file()
        {
            issues.push(format!("{} ticket file is missing", ticket.ticket_id));
        }
        if ticket.qa_required {
            qa_required_count += 1;
        } else {
            issues.push(format!("{} qa_required is false", ticket.ticket_id));
        }
        if ticket.failure_route_required {
            failure_route_required_count += 1;
        } else {
            issues.push(format!(
                "{} failure_route_required is false",
                ticket.ticket_id
            ));
        }
        let command_text = ticket.required_commands.join("\n");
        if !command_text.contains("taiko_cli qa run")
            || !command_text.contains("taiko_cli qa verdict")
        {
            issues.push(format!("{} lacks QA command evidence", ticket.ticket_id));
        }
        for doc in &ticket.acceptance_docs {
            if !root.join(doc).exists() {
                issues.push(format!(
                    "{} acceptance doc missing: {}",
                    ticket.ticket_id, doc
                ));
            }
        }
        let missing_deps = ticket
            .depends_on
            .iter()
            .filter(|dep| {
                if dep.starts_with("TKT-") {
                    ticket_status.get(dep.as_str()) != Some(&"Done")
                } else if dep.starts_with("GATE-") {
                    !gate_ids.contains(&dep.as_str()) || !gate_report_exists(root, dep)
                } else {
                    true
                }
            })
            .count();
        if missing_deps == 0 && next_ticket.is_none() && include_plan {
            next_ticket = Some(ticket.ticket_id.clone());
        } else if missing_deps > 0 {
            blocked_count += 1;
        }
    }

    let first_feature_ticket = tickets.first().map(|ticket| ticket.ticket_id.clone());
    if first_feature_ticket.as_deref() != Some("TKT-0005") {
        issues.push("first feature ticket must be TKT-0005".to_string());
    }

    let verdict = if issues.is_empty() { "pass" } else { "reject" }.to_string();
    Ok(Phase1FeaturePlanReport {
        verdict,
        manifest,
        feature_ticket_count: tickets.len(),
        first_feature_ticket,
        next_ticket,
        blocked_count,
        qa_required_count,
        failure_route_required_count,
        issues,
    })
}

fn toml_string(value: Option<&String>) -> Option<String> {
    let value = value?.trim();
    Some(value.trim_matches('"').to_string())
}

fn toml_bool(value: Option<&String>) -> bool {
    value
        .map(|value| value.trim().eq_ignore_ascii_case("true"))
        .unwrap_or(false)
}

fn toml_array(value: Option<&String>) -> Vec<String> {
    let Some(value) = value else {
        return Vec::new();
    };
    let mut result = Vec::new();
    let mut rest = value.as_str();
    while let Some(start) = rest.find('"') {
        rest = &rest[start + 1..];
        let Some(end) = rest.find('"') else {
            break;
        };
        result.push(rest[..end].to_string());
        rest = &rest[end + 1..];
    }
    result
}

fn render_phase1_feature_plan(report: &Phase1FeaturePlanReport, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"verdict\":\"{}\",\"manifest\":\"{}\",\"feature_ticket_count\":{},\"first_feature_ticket\":{},\"next_ticket\":{},\"blocked_count\":{},\"qa_required_count\":{},\"failure_route_required_count\":{},\"issues\":{}}}",
            escape_json(&report.verdict),
            escape_json(&report.manifest),
            report.feature_ticket_count,
            optional_string_json(report.first_feature_ticket.as_deref()),
            optional_string_json(report.next_ticket.as_deref()),
            report.blocked_count,
            report.qa_required_count,
            report.failure_route_required_count,
            string_array_json(&report.issues)
        ),
        OutputFormat::Markdown => format!(
            "verdict: {}\nmanifest: {}\nfeature tickets: {}\nfirst feature ticket: {}\nnext ticket: {}\nblocked count: {}\nissues: {}",
            report.verdict,
            report.manifest,
            report.feature_ticket_count,
            report.first_feature_ticket.as_deref().unwrap_or("none"),
            report.next_ticket.as_deref().unwrap_or("none"),
            report.blocked_count,
            report.issues.join(", ")
        ),
    }
}

fn render_fixture_validation(
    report: &taiko_chart::FixtureValidationReport,
    format: OutputFormat,
) -> String {
    match format {
        OutputFormat::Json => report.to_json(),
        OutputFormat::Markdown => report.to_markdown(),
    }
}

fn render_chart_inspection(
    report: &taiko_chart::ChartInspectionReport,
    format: OutputFormat,
) -> String {
    match format {
        OutputFormat::Json => report.to_json(),
        OutputFormat::Markdown => report.to_markdown(),
    }
}

fn render_timing_analysis(report: &TimingAnalysisReport, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => report.to_json(),
        OutputFormat::Markdown => report.to_markdown(),
    }
}

fn timing_input_from_headless(
    report: &HeadlessAutoplayReport,
    source: &str,
) -> HeadlessTimingInput {
    let fixtures = report
        .fixtures
        .iter()
        .map(|fixture| HeadlessTimingFixtureInput {
            fixture_id: fixture.fixture_id.clone(),
            path: fixture.path.clone(),
            verdict: fixture.verdict.clone(),
            note_count: fixture.note_count,
            scheduled_event_count: fixture.scheduled_event_count,
            hit_count: fixture.hit_count,
            miss_count: fixture.miss_count,
            song_end_reached: fixture.song_end_reached,
            issues: fixture.issues.clone(),
        })
        .collect::<Vec<_>>();

    HeadlessTimingInput {
        scope: report.scope.clone(),
        source: source.to_string(),
        verdict: report.verdict.clone(),
        fixture_count: report.fixture_count,
        total_note_count: report.total_note_count,
        total_scheduled_event_count: report.total_scheduled_event_count,
        total_hit_count: report.total_hit_count,
        total_miss_count: report.total_miss_count,
        fixtures,
        issues: report.issues.clone(),
    }
}

fn render_headless_autoplay(
    report: &taiko_runtime::HeadlessAutoplayReport,
    format: OutputFormat,
) -> String {
    match format {
        OutputFormat::Json => report.to_json(),
        OutputFormat::Markdown => report.to_markdown(),
    }
}

fn render_tickets(tickets: &[Ticket], format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => {
            let items = tickets
                .iter()
                .map(ticket_json)
                .collect::<Vec<_>>()
                .join(",");
            format!("{{\"tickets\":[{items}],\"count\":{}}}", tickets.len())
        }
        OutputFormat::Markdown => tickets
            .iter()
            .map(|ticket| format!("- {} [{}]: {}", ticket.id, ticket.status, ticket.title))
            .collect::<Vec<_>>()
            .join("\n"),
    }
}

fn render_gates(gates: &[Gate], format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => {
            let items = gates.iter().map(gate_json).collect::<Vec<_>>().join(",");
            format!("{{\"gates\":[{items}],\"count\":{}}}", gates.len())
        }
        OutputFormat::Markdown => gates
            .iter()
            .map(|gate| format!("- {} [{}]: {}", gate.id, gate.status, gate.title))
            .collect::<Vec<_>>()
            .join("\n"),
    }
}

fn render_next(selection: &NextSelection, format: OutputFormat) -> String {
    match (selection, format) {
        (NextSelection::Selected { ticket_id, reason }, OutputFormat::Json) => format!(
            "{{\"verdict\":\"ready\",\"ticket_id\":\"{}\",\"reason\":\"{}\"}}",
            escape_json(ticket_id),
            escape_json(reason)
        ),
        (NextSelection::Block { reason }, OutputFormat::Json) => format!(
            "{{\"verdict\":\"block\",\"ticket_id\":null,\"reason\":\"{}\"}}",
            escape_json(reason)
        ),
        (NextSelection::Selected { ticket_id, reason }, OutputFormat::Markdown) => {
            format!("- verdict: `ready`\n- ticket_id: `{ticket_id}`\n- reason: {reason}")
        }
        (NextSelection::Block { reason }, OutputFormat::Markdown) => {
            format!("- verdict: `block`\n- ticket_id: `null`\n- reason: {reason}")
        }
    }
}

fn render_loop_run_once_plan(plan: &LoopRunOncePlan, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"run_id\":\"{}\",\"mode\":\"{}\",\"state\":\"{}\",\"verdict\":\"{}\",\"selected_ticket\":{},\"next_action\":\"{}\",\"reason\":\"{}\",\"branch\":{},\"implementation_worktree\":{},\"review_worktree\":{},\"qa_worktree\":{},\"session_metadata_path\":{},\"controller_report_json\":\"{}\",\"controller_report_markdown\":\"{}\",\"next_codex_prompt\":\"{}\",\"required_commands\":{},\"missing_gate_evidence\":{},\"open_failures\":{},\"artifacts_written\":{}}}",
            escape_json(&plan.run_id),
            escape_json(&plan.mode),
            escape_json(&plan.state),
            escape_json(&plan.verdict),
            optional_string_json(plan.selected_ticket.as_deref()),
            escape_json(&plan.next_action),
            escape_json(&plan.reason),
            optional_string_json(plan.branch.as_deref()),
            optional_string_json(plan.implementation_worktree.as_deref()),
            optional_string_json(plan.review_worktree.as_deref()),
            optional_string_json(plan.qa_worktree.as_deref()),
            optional_string_json(plan.session_metadata_path.as_deref()),
            escape_json(&plan.controller_report_json),
            escape_json(&plan.controller_report_markdown),
            escape_json(&plan.next_codex_prompt),
            string_array_json(&plan.required_commands),
            string_array_json(&plan.missing_gate_evidence),
            string_array_json(&plan.open_failures),
            string_array_json(&plan.artifacts_written)
        ),
        OutputFormat::Markdown => format!(
            "# Loop run-once controller plan\n\n- run_id: `{}`\n- mode: `{}`\n- state: `{}`\n- verdict: `{}`\n- selected_ticket: `{}`\n- next_action: `{}`\n- reason: {}\n- branch: `{}`\n- implementation_worktree: `{}`\n- review_worktree: `{}`\n- qa_worktree: `{}`\n- session_metadata_path: `{}`\n- controller_report_json: `{}`\n- controller_report_markdown: `{}`\n- next_codex_prompt: `{}`\n- missing_gate_evidence: {}\n- open_failures: {}\n- artifacts_written: {}",
            plan.run_id,
            plan.mode,
            plan.state,
            plan.verdict,
            plan.selected_ticket.as_deref().unwrap_or("none"),
            plan.next_action,
            plan.reason,
            plan.branch.as_deref().unwrap_or("none"),
            plan.implementation_worktree.as_deref().unwrap_or("none"),
            plan.review_worktree.as_deref().unwrap_or("none"),
            plan.qa_worktree.as_deref().unwrap_or("none"),
            plan.session_metadata_path.as_deref().unwrap_or("none"),
            plan.controller_report_json,
            plan.controller_report_markdown,
            plan.next_codex_prompt,
            plan.missing_gate_evidence.join(", "),
            plan.open_failures.join(", "),
            plan.artifacts_written.join(", "),
        ),
    }
}

fn render_gate_verdict(verdict: &GateVerdict, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"gate_id\":\"{}\",\"verdict\":\"{}\",\"missing_inputs\":{},\"present_inputs\":{},\"pass_criteria_count\":{}}}",
            escape_json(&verdict.gate_id),
            escape_json(&verdict.verdict),
            string_array_json(&verdict.missing_inputs),
            string_array_json(&verdict.present_inputs),
            verdict.pass_criteria_count
        ),
        OutputFormat::Markdown => format!(
            "gate: {}\nverdict: {}\nmissing inputs: {}\npresent inputs: {}\npass criteria: {}",
            verdict.gate_id,
            verdict.verdict,
            verdict.missing_inputs.join(", "),
            verdict.present_inputs.join(", "),
            verdict.pass_criteria_count
        ),
    }
}

fn render_status(status: &LoopStatus, format: OutputFormat) -> String {
    match format {
        OutputFormat::Json => format!(
            "{{\"autonomy_score_estimate\":{},\"ready_tickets\":{},\"blocked_tickets\":{},\"done_tickets\":{},\"missing_gate_evidence\":{},\"next_selected_ticket\":{},\"open_failures\":{}}}",
            status.autonomy_score_estimate,
            string_array_json(&status.ready_tickets),
            string_array_json(&status.blocked_tickets),
            string_array_json(&status.done_tickets),
            string_array_json(&status.missing_gate_evidence),
            optional_string_json(status.next_selected_ticket.as_deref()),
            string_array_json(&status.open_failures)
        ),
        OutputFormat::Markdown => format!(
            "autonomy score estimate: {}\nready tickets: {}\nblocked tickets: {}\nmissing gate evidence: {}\nnext selected ticket: {}\nopen failures: {}",
            status.autonomy_score_estimate,
            status.ready_tickets.join(", "),
            status.blocked_tickets.join(", "),
            status.missing_gate_evidence.join(", "),
            status.next_selected_ticket.as_deref().unwrap_or("none"),
            status.open_failures.join(", ")
        ),
    }
}

fn ticket_json(ticket: &Ticket) -> String {
    format!(
        "{{\"id\":\"{}\",\"title\":\"{}\",\"status\":\"{}\",\"owner_session\":\"{}\",\"review_session\":\"{}\",\"dependencies\":{},\"required_checks\":{},\"evidence_requirements\":{},\"path\":\"{}\"}}",
        escape_json(&ticket.id),
        escape_json(&ticket.title),
        escape_json(&ticket.status),
        escape_json(&ticket.owner_session),
        escape_json(&ticket.review_session),
        string_array_json(&ticket.dependencies),
        string_array_json(&ticket.required_checks),
        string_array_json(&ticket.evidence_requirements),
        escape_json(&ticket.path)
    )
}

fn gate_json(gate: &Gate) -> String {
    format!(
        "{{\"id\":\"{}\",\"title\":\"{}\",\"status\":\"{}\",\"owner\":\"{}\",\"reviewer\":\"{}\",\"scorecard_impact\":{},\"required_inputs\":{},\"pass_criteria\":{},\"output_path\":\"{}\",\"next_ticket_transition\":\"{}\",\"path\":\"{}\"}}",
        escape_json(&gate.id),
        escape_json(&gate.title),
        escape_json(&gate.status),
        escape_json(&gate.owner),
        escape_json(&gate.reviewer),
        string_array_json(&gate.scorecard_impact),
        string_array_json(&gate.required_inputs),
        string_array_json(&gate.pass_criteria),
        escape_json(&gate.output_path),
        escape_json(&gate.next_ticket_transition),
        escape_json(&gate.path)
    )
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
    use super::{branch_name_for_ticket, parse_gate, parse_ticket, slugify};
    use std::path::Path;

    #[test]
    fn parses_ticket_heading_and_status() {
        let text = "# TKT-9999: Example\n\nStatus: Ready\nOwner session: A\nReview session: B\n";
        let ticket = parse_ticket(Path::new("."), Path::new(".loop/tickets/TKT-9999.md"), text);
        assert_eq!(ticket.id, "TKT-9999");
        assert_eq!(ticket.title, "Example");
        assert_eq!(ticket.status, "Ready");
    }

    #[test]
    fn parses_gate_inputs() {
        let text = "# GATE-9999: Example\n\nStatus: active\nOwner: A\nReviewer: B\n\n## Required inputs\n\n- `AGENTS.md`\n\n## Pass criteria\n\n| Check | Required result |\n|---|---|\n| Exists | Present |\n";
        let gate = parse_gate(Path::new("."), Path::new(".loop/gates/GATE-9999.md"), text);
        assert_eq!(gate.id, "GATE-9999");
        assert_eq!(gate.required_inputs, vec!["AGENTS.md"]);
        assert_eq!(gate.pass_criteria, vec!["Exists"]);
    }

    #[test]
    fn slugifies_controller_branch_names() {
        let text = "# TKT-0050: QA regression gate MVP\n\nStatus: Blocked\nOwner session: Test Infrastructure Session\nReview session: Design Review Session\n";
        let ticket = parse_ticket(Path::new("."), Path::new(".loop/tickets/TKT-0050.md"), text);
        assert_eq!(slugify("QA regression gate MVP"), "qa-regression-gate-mvp");
        assert_eq!(
            branch_name_for_ticket(&ticket),
            "test/TKT-0050-qa-regression-gate-mvp"
        );
    }
}
