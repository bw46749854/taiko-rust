#!/usr/bin/env python3
"""Validate Rust preflight runtime evidence files.

This validator checks the evidence contract even when the preflight itself
reported reject or block. Pass `--require-pass` only when the caller needs a
successful gate verdict.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LOOP_CLI_IDS = [
    'cargo_version',
    'rustc_version',
    'cargo_fmt',
    'cargo_clippy',
    'cargo_test',
    'rust_workspace_static',
    'loop_inspect_tickets',
    'loop_inspect_gates',
    'loop_next',
    'loop_gate_0000',
    'loop_report_status',
]

CURRENT_PACKAGE_EXTRA_IDS = [
    'fixture_validate',
    'fixture_inspect',
    'headless_autoplay',
    'timing_analyze',
    'failure_ingest',
    'ticket_propose',
    'ticket_validate',
    'qa_run',
    'qa_verdict',
    'phase1_feature_validate',
    'phase1_feature_plan',
]

ALLOWED_VERDICTS = {'pass', 'reject', 'block'}
ALLOWED_STATUSES = {'pass', 'fail', 'block'}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f'missing evidence JSON: {path}')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        fail(f'malformed evidence JSON: {path}: {exc}')


def required_ids(scope: str) -> list[str]:
    if scope == 'loop-cli':
        return LOOP_CLI_IDS
    if scope == 'current-package':
        return LOOP_CLI_IDS + CURRENT_PACKAGE_EXTRA_IDS
    fail(f'unsupported scope requirement: {scope}')
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, help='Path to rust_preflight_report.json')
    parser.add_argument('--require-scope', choices=['loop-cli', 'current-package'])
    parser.add_argument('--require-pass', action='store_true')
    args = parser.parse_args()

    path = Path(args.path)
    report = load_json(path)
    base_dir = path.parent

    if report.get('schema_version') != 'rust-preflight.v1':
        fail('schema_version must be rust-preflight.v1')

    scope = report.get('scope')
    if scope not in {'loop-cli', 'current-package'}:
        fail(f'unsupported scope in report: {scope}')

    if args.require_scope:
        required_rank = {'loop-cli': 1, 'current-package': 2}
        if required_rank[scope] < required_rank[args.require_scope]:
            fail(f'report scope {scope} does not satisfy required scope {args.require_scope}')

    verdict = report.get('verdict')
    if verdict not in ALLOWED_VERDICTS:
        fail(f'unsupported verdict: {verdict}')
    if args.require_pass and verdict != 'pass':
        fail(f'preflight verdict is {verdict}, expected pass')

    summary = report.get('summary')
    if not isinstance(summary, dict):
        fail('summary must be an object')
    for key in ['total', 'passed', 'failed', 'blocked']:
        if not isinstance(summary.get(key), int):
            fail(f'summary.{key} must be an integer')

    commands = report.get('commands')
    if not isinstance(commands, list) or not commands:
        fail('commands must be a non-empty list')

    command_by_id = {}
    for command in commands:
        if not isinstance(command, dict):
            fail('each command entry must be an object')
        command_id = command.get('id')
        if not isinstance(command_id, str) or not command_id:
            fail('command.id must be a non-empty string')
        if command_id in command_by_id:
            fail(f'duplicate command id: {command_id}')
        command_by_id[command_id] = command
        if command.get('status') not in ALLOWED_STATUSES:
            fail(f'{command_id} has unsupported status: {command.get("status")}')
        if not isinstance(command.get('exit_code'), int):
            fail(f'{command_id} exit_code must be an integer')
        if not isinstance(command.get('duration_ms'), int):
            fail(f'{command_id} duration_ms must be an integer')
        for log_key in ['stdout_log', 'stderr_log']:
            log_value = command.get(log_key)
            if not isinstance(log_value, str) or not log_value:
                fail(f'{command_id} missing {log_key}')
            log_path = Path(log_value)
            if not log_path.is_absolute():
                log_path = Path.cwd() / log_path
            if not log_path.is_file():
                alt = base_dir / log_value
                if alt.is_file():
                    log_path = alt
                else:
                    fail(f'{command_id} missing log file: {log_value}')

    for command_id in required_ids(args.require_scope or scope):
        if command_id not in command_by_id:
            fail(f'missing required command evidence: {command_id}')

    counted_total = len(commands)
    counted_passed = sum(1 for c in commands if c.get('status') == 'pass')
    counted_failed = sum(1 for c in commands if c.get('status') == 'fail')
    if summary['total'] != counted_total:
        fail('summary.total does not match command count')
    if summary['passed'] != counted_passed:
        fail('summary.passed does not match command statuses')
    if summary['failed'] != counted_failed:
        fail('summary.failed does not match command statuses')
    if verdict == 'pass' and counted_failed != 0:
        fail('pass verdict cannot contain failed commands')

    markdown = base_dir / 'rust_preflight_report.md'
    commands_tsv = base_dir / 'commands.tsv'
    if not markdown.is_file():
        fail(f'missing markdown report: {markdown}')
    if not commands_tsv.is_file():
        fail(f'missing commands TSV: {commands_tsv}')

    print('runtime evidence files check passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
