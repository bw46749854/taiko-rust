# PR Review Template

Status: canonical
Purpose: standardize Design Review Session output for a ticket implementation PR or branch diff.

## 1. Review metadata

| Field | Value |
|---|---|
| Ticket |  |
| Implementation branch/worktree |  |
| Reviewer session | Design Review Session |
| Review date |  |
| Reviewed commit/range |  |

## 2. Required read set confirmation

- [ ] `AGENTS.md`
- [ ] `.loop/tickets/<ticket-id>.md`
- [ ] Relevant design documents listed in the ticket
- [ ] Relevant OpenTaiko research/adoption decision documents
- [ ] Relevant coverage matrix and fixture traceability documents

## 3. Scope review

- [ ] Diff is limited to the ticket scope.
- [ ] No drive-by refactor is present.
- [ ] No implementation Session self-approval is present.
- [ ] No user song, audio, image, video, or copyrighted chart asset is committed.

## 4. Architecture review

- [ ] Changed crates match `AGENTS.md` canonical crate boundaries.
- [ ] Pure crates do not depend on platform adapters.
- [ ] Runtime behavior is shared by playable and headless execution paths.
- [ ] Parser/report behavior does not silently ignore unsupported normal-play commands.

## 5. Evidence review

Attach or reference the exact command log.

```text
commands:
results:
artifacts:
```

Required evidence status:

| Evidence | Status | Notes |
|---|---|---|
| `cargo fmt --check` |  |  |
| `cargo clippy --workspace --all-targets --all-features -- -D warnings` |  |  |
| `cargo test --workspace --all-features` |  |  |
| fixture validation |  |  |
| headless autoplay |  |  |
| timing analyzer |  |  |
| compatibility report delta |  |  |

## 6. Findings

| Severity | Finding | Required action |
|---|---|---|
| Blocker/Major/Minor |  |  |

## 7. Decision

Choose exactly one:

- [ ] Approved for QA / Regression Session
- [ ] Changes requested
- [ ] Blocked due to missing evidence
- [ ] Blocked due to specification ambiguity

## 8. Remaining risk list

- 
