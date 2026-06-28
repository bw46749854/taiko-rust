# Notice

Status: canonical

This repository is a clean-room Rust implementation project for an OpenTaiko-compatible Phase1 rhythm game and loop-engineering control system.

## Third-party relationship

- OpenTaiko is a separate upstream project.
- This repository does not vendor OpenTaiko source code.
- This repository does not include OpenTaiko skins, songs, charts, audio, images, videos, or other game assets.
- Compatibility references are used only to define behavior contracts and test expectations for a new implementation.

## Asset notice

Commercial songs, copyrighted audio, copyrighted charts, copyrighted images, copyrighted videos, and third-party skins must not be committed. Development assets are handled outside the repository and will be introduced later through the deterministic asset-bundle contract.

## Automation notice

GitHub Actions verifies, gates, merges eligible PRs, advances tickets, and emits handoff artifacts. GitHub Actions does not run Codex or GPT workers and does not require `OPENAI_API_KEY` or `CODEX_API_KEY` for gate duties.
