# Auto-Merge Candidate Reports

Status: canonical

`loop-controller` writes candidate discovery artifacts here.

Expected files:

- `candidate_plan.json`
- `candidate_plan.md`
- `open_prs.json`

These artifacts are deterministic controller evidence. They do not contain OpenAI API output and do not require `OPENAI_API_KEY` or `CODEX_API_KEY`.
