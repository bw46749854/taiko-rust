# 87. Secret and Network Policy

Status: canonical

## Purpose

This policy prevents the autonomous loop from leaking secrets, copying user-selected assets, or silently depending on uncontrolled network access. It applies to Codex Cloud, Codex CLI/App, GitHub Actions, and any local runner used for Phase1.

## Default position

| Area | Default |
|---|---|
| Codex Cloud agent internet access | off |
| Setup script internet access | allowed only for toolchain/dependency installation |
| Runtime ticket commands | no public internet required |
| Normal implementation secrets | none |
| User-selected song assets | never committed |
| Commercial song/audio/skin/chart assets | never committed |
| API keys in repo-controlled CI jobs | never job-level environment variables |

## Secrets

Normal ticket implementation does not require `OPENAI_API_KEY`, `CODEX_API_KEY`, `GITHUB_TOKEN`, `GH_TOKEN`, cloud credentials, package-publishing tokens, or private registry tokens.

The repository-scoped `.codex/config.toml` excludes common secret names from subprocess environments and denies `.env`-like files through the local Codex permission profile. This is defense in depth; it does not replace GitHub secret hygiene.

## GitHub Actions secret rule

Do not set `OPENAI_API_KEY` or `CODEX_API_KEY` as a job-level environment variable in any workflow that checks out or runs repository-controlled code.

## Plus-plan Step20 rule

For this package, `openai/codex-action@v1` is not used for normal implementation, review, QA, or controller work. GitHub Actions must not call AI workers. GitHub Actions may only run deterministic repository checks, create review-request comments, upload artifacts, and later perform mechanical auto-merge/advance.

The reason is economic and operational, not data-safety oriented: a GitHub Actions AI worker requires an API-key path, while the project target is ChatGPT-plan Codex usage through Codex Cloud, Codex App Automations, or Codex CLI.

## Codex review workflow

`.github/workflows/codex-review.yml` is manual by default. It posts a deterministic detached-review request and does not call an AI worker, approve, or merge PRs.

The review workflow must remain constrained:

- no job-level `OPENAI_API_KEY` or `CODEX_API_KEY`;
- no `openai-api-key` workflow input;
- no `uses: openai/codex-action@v1` step;
- no `cargo`, test, or repository-controlled build command after any secret is exposed;
- feedback posting uses `github.token` only;
- PR approval remains unavailable to the implementation session.

## Network policy

Codex Cloud agent internet access stays off for normal implementation and QA tasks. The setup script may use internet access because Rust installation and dependency fetch happen before the agent phase.

When a future ticket proves that agent internet is required, the allowed domains must be explicitly documented in that ticket and reviewed separately. The default allowlist for setup-only dependency installation is:

```text
static.rust-lang.org
sh.rustup.rs
crates.io
index.crates.io
github.com
githubusercontent.com
objects.githubusercontent.com
```

Do not enable unrestricted agent internet access for OpenTaiko source investigation inside implementation sessions. Source investigation belongs to the Spec Extraction Session and must be summarized in committed research docs.

## Asset policy

The repository must not contain commercial song, audio, image, video, skin, or chart assets. User-selected song validation uses local manifests only.

The committed checker is:

```bash
scripts/validate_no_user_assets.sh
```

Any PR that adds media/chart-like files outside synthetic fixtures must be blocked unless the file is demonstrably synthetic, text-only, and covered by the fixture manifest.

## Local runner policy

A local runner may contain user-selected songs for validation, but those paths must stay outside Git worktrees. Local manifests may point to files on the operator machine; the files themselves must not be copied into the repository.

## Failure handling

| Violation | Verdict | Required transition |
|---|---|---|
| Secret committed | block | remove secret, rotate credential, create incident report |
| Job-level API key or `openai/codex-action@v1` in repo-controlled workflow | block | remove API-key worker and use Codex Cloud/App Automation instead |
| Agent internet enabled without ticket evidence | block | disable internet or create reviewed environment ticket |
| User-selected or commercial asset committed | block | remove asset and rerun asset validation |
| Runtime command depends on internet | reject | remove dependency or create explicit reviewed exception |

A blocked security/network violation must not be converted into a docs-only pass.


## Step21 auto-merge rule

The loop-controller workflow uses `GITHUB_TOKEN` permissions for repository mechanics only. It must not use `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1`. AI implementation remains on Codex Cloud/App/CLI surfaces authenticated through the ChatGPT plan.
