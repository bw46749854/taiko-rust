# 83. Codex Surface Decision

Status: canonical

## Purpose

Fix the execution surface for autonomous Phase1 loop operation before gameplay implementation starts.

This document removes ambiguity between Codex Cloud, Codex CLI, Codex App, GitHub Actions, and GitHub PR review.

## Adopted execution surface

| Loop role | Primary surface | Reason |
|---|---|---|
| Control Session | Codex Cloud task or Codex CLI in `worktrees/control` | Selects next ticket, records transition evidence, invokes orchestration scripts. |
| Ticket Implementation Session | Codex Cloud task, Codex App Automation, or Codex CLI signed in with ChatGPT | Cloud/App/CLI can work on one ticket branch, run terminal commands, and produce a PR-ready diff without an API-key worker. |
| Design Review Session | Codex GitHub review or separate Codex Cloud review task | Review must be detached from implementation worktree and implementation thread. |
| QA / Regression Session | GitHub Actions plus separate Codex Cloud/CLI QA worktree | QA must run machine-readable gates and produce pass/reject/block evidence. |
| Local user-song validation | Codex CLI or Codex App on operator machine | User-selected assets are not committed and remain local manifest paths only. |
| Codex App Automations | Primary heartbeat surface after Step20 | Recurring low-frequency task reads the generated controller prompt and advances one ticket without `OPENAI_API_KEY`. |

## Source-of-truth rule

GitHub is the shared durable state for autonomous loop operation:

- branch state;
- PR state;
- CI status;
- Codex review comments;
- merge status;
- committed ticket/gate/session-log evidence.

Local worktrees are disposable execution sandboxes. They must not become the only record of a pass/reject/block decision.

## Rust environment rule

The canonical Rust runtime check is GitHub Actions and Codex Cloud. A local Rust installation is useful but not required for loop bootstrap.

A ticket cannot be accepted as Done when all Rust-dependent commands are skipped. A missing local Rust toolchain is recorded as environment limitation, not as ticket pass.

## Codex Cloud environment rule

Codex Cloud is the first execution surface for `TKT-0000` and `TKT-0001` after the package is pushed to a private GitHub repository. The Cloud environment must install or pin the Rust toolchain before `TKT-0001` evidence is collected.

Required Cloud setup policy:

- repository connected to Codex Cloud;
- setup script installs or pins Rust;
- setup script may use internet access for dependencies;
- agent phase should remain network-restricted unless a ticket explicitly requires online source inspection;
- secrets are not relied on during the agent phase;
- `AGENTS.md` remains the repository-level operating rule file.

## Codex GitHub review rule

Every implementation PR requires either:

1. native Codex GitHub review triggered by `@codex review` or automatic reviews; or
2. detached Codex Cloud/App review using `.github/codex/prompts/review.md`, with `.github/workflows/codex-review.yml` posting a deterministic review request.

The Codex review is not the same as QA. It is a design/diff risk review. QA must still produce machine-readable `taiko_cli qa ...` evidence.

## Step20 Plus-plan update

The API-key GitHub Action worker is not the primary surface for this project. GitHub Actions must not invoke `openai/codex-action@v1` for normal implementation or review. AI execution remains on Codex Cloud, Codex App Automations, or Codex CLI signed in with ChatGPT. GitHub Actions remain deterministic: static checks, Rust preflight, QA gates, metadata/path-policy gates, review-request comments, and later auto-merge.

## CLI rule

Codex CLI is retained for:

- local reproduction;
- control-session shell orchestration;
- user-selected song validation;
- emergency repair when GitHub/Codex Cloud cannot run.

CLI work must still use the same branch, worktree, PR, and QA verdict contract in `docs/84_github_pr_loop_contract.md`.

## References

- Codex Cloud overview: <https://developers.openai.com/codex/cloud>
- Codex Cloud environments: <https://developers.openai.com/codex/cloud/environments>
- Codex GitHub review: <https://developers.openai.com/codex/integrations/github>
- Codex App Automations: <https://developers.openai.com/codex/app/automations>
- Codex non-interactive automation security: <https://developers.openai.com/codex/noninteractive>
