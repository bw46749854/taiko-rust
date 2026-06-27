## Ticket

- Ticket ID:
- Ticket file: `.loop/tickets/`
- Owner session:
- Review session:
- Branch:
- Worktree:

## Scope

- 

## Required checks

```bash
# paste ticket-required commands and mark pass/reject/block evidence paths
```

## Evidence

- Plan:
- Plan review:
- Command log:
- QA verdict JSON:
- Gate report / session log:
- Session metadata:

## QA transition

- Verdict: pass / reject / block
- Verdict source:
- Next-ticket transition:

## Asset policy

- [ ] No commercial song, audio, image, video, skin, or chart asset was committed.
- [ ] User-selected song validation uses local manifest paths only.
- [ ] `scripts/validate_no_user_assets.sh` passed or is not relevant to this docs-only PR.

## Self-approval prevention

- [ ] Implementation Session is not the same as Design Review Session.
- [ ] Implementation Session is not the same as QA / Regression Session.
- [ ] Review/QA evidence is recorded in text or JSON.

## Codex review

- [ ] Native `@codex review` requested, automatic Codex review enabled, or `.github/workflows/codex-review.yml` run manually.


## Public repository safety

- [ ] No secrets, tokens, `.env` files, OAuth credentials, service-account JSON, signed URLs, or private Drive URLs were committed.
- [ ] No private Drive asset bundle or extracted asset directory was committed.
- [ ] No commercial song, copyrighted audio, chart, image, video, or third-party skin asset was committed.
- [ ] No AI worker in GitHub Actions was introduced; `OPENAI_API_KEY`, `CODEX_API_KEY`, and `openai/codex-action@v1` remain unused by workflows.
- [ ] `pull_request_target` was not introduced.
- [ ] `scripts/check_public_repository_static.py` passed.
