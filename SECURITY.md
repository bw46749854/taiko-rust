# Security Policy

Status: canonical

## Supported branch

Security handling applies to the active protected branch used by the operations migration rail and Phase1 implementation.

## Reporting

Report security issues by opening a private security advisory in GitHub or by using the repository owner's designated private reporting channel. Do not place credentials, private Drive links, copyrighted assets, or exploit details in public issues.

## Repository safety rules

- Do not commit secrets, tokens, `.env` files, OAuth credentials, service-account JSON files, signed URLs, or private asset URLs.
- Do not commit commercial songs, copyrighted charts, audio, images, videos, or third-party skins.
- Do not add `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1` to GitHub Actions for normal loop operation.
- Do not use `pull_request_target` workflows in this repository.
- Privileged GitHub Actions workflows must not checkout or execute untrusted PR head code.

## Gate response

A PR that violates the public repository policy receives a `block` verdict. The repair route removes the offending material, rotates exposed credentials outside this repository, and records evidence before the ticket can continue.
