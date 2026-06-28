# 97. Public Repository Hardening

Status: canonical

## Purpose

This document defines the public-readiness contract for the operations migration rail. The repository may become public only after this contract, `operations/public_repository_policy.toml`, and `scripts/check_public_repository_static.py` pass.

## Repository visibility rule

The repository remains private during `OPS-0003`. Public visibility is unlocked later by `GATE-OPS-0000` after the full operations migration rail completes.

## Required public files

- `LICENSE`
- `NOTICE.md`
- `THIRD_PARTY_NOTICES.md`
- `SECURITY.md`
- `operations/public_repository_policy.toml`
- `scripts/check_public_repository_static.py`
- `.github/dependabot.yml`

## Asset rule

The repository must not contain commercial songs, copyrighted audio, copyrighted charts, copyrighted images, copyrighted videos, third-party skins, private Drive archives, local user-song payloads, or extracted asset bundles. User-selected validation may use manifests that point to external files, but asset payloads remain untracked.

## Secret rule

The repository must not contain secrets, tokens, OAuth credentials, service-account JSON, `.env` files, signed URLs, or private asset URLs. GitHub Actions uses `GITHUB_TOKEN` for repository mechanics only.

## AI worker rule

GitHub Actions is a verifier, gate, merge controller, ticket advancement controller, and handoff artifact generator. It must not run Codex or GPT workers and must not require `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1`.

## Workflow rule

- `pull_request_target` is forbidden. Plain rule: pull_request_target is forbidden.
- Workflow permissions must be explicitly scoped.
- Read-only verification workflows use `contents: read`.
- Write permissions are limited to loop-controller and deterministic review-comment workflows.
- Privileged workflows must not execute untrusted PR head code.

## Publication gate

`OPS-0003` adds the public-readiness static check. Later tickets add deterministic asset fetching, Actions gate normalization, auto-merge candidate discovery, ticket advancement, and worker handoff. Public visibility is not enabled until all migration checks pass.
