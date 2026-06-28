# Auto-Merge Candidate Schema

Status: canonical

`reports/loop/candidates/candidate_plan.json` is produced by `scripts/select_auto_merge_candidate.py`.

Required top-level fields:

- `schema`: must reference this document.
- `verdict`: `pass`, `reject`, or `block`.
- `selected_pr`: selected PR record when `verdict` is `pass`; otherwise `null`.
- `required_label`: currently `loop:automerge`.
- `base_branch`: currently `main`.
- `required_checks`: exact GitHub required check contexts from `operations/auto_merge_policy.toml`.
- `max_merge_candidates_per_run`: currently `1`.
- `reasons`: controller-readable reason list.
- `candidates`: classified PR records.

A candidate record contains:

- `number`
- `title`
- `baseRefName`
- `headRefName`
- `headRefOid`
- `labels`
- `ticket_id`
- `metadata_path`
- `qa_verdict_path`
- `verdict`
- `reasons`
- `required_checks`

`pass` requires exactly one labeled PR with `loop:automerge`, base branch `main`, non-draft status, PR head SHA, ticket id, session metadata path, QA verdict path, and every required check in a successful state.

`block` is used when evidence is still pending, no labeled PR exists, a draft PR is waiting, required checks are pending, or multiple passing PRs would otherwise be mergeable in the same controller run.

`reject` is used when a labeled PR violates a fixed policy such as wrong base branch, missing ticket id, missing metadata path, missing QA path, missing PR head SHA, or a failed required check.
