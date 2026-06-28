# 02. Documentation Language Policy

Status: canonical
Last updated: 2026-06-28

## 1. Purpose

This policy keeps the autonomous loop readable by separated AI sessions, GitHub Actions, scripts, reviewers, and future maintainers. The repository may include Japanese explanatory material, but canonical operational meaning must remain available in English before tickets, gates, prompts, scripts, schemas, or implementation work depend on it.

## 2. Canonical language

English is the canonical language for operational repository surfaces, including:

- `docs/` files that define requirements, gates, contracts, policies, acceptance criteria, QA routes, or loop operation.
- `prompts/` files used to start or continue Codex, Control, Implementation, Review, QA, or automation sessions.
- `.loop/tickets/` ticket files and `.loop/gates/` gate files.
- `scripts/`, workflow text, schema documentation, report templates, fixtures metadata, and command examples.
- Rust code comments, public API documentation, crate documentation, and CLI help text.
- `README.md`, `AGENTS.md`, and other root-level operational guidance.

## 3. Japanese explanatory documents

Japanese explanatory documents may exist only when they are explicitly marked as translations or non-canonical explanatory material. Use one of these forms:

- `*.ja.md` for a Japanese translation of an English canonical document.
- An explicit header such as `Status: translation` or `Status: non-canonical explanation` near the top of the file.
- A pointer to the English canonical source, for example: `Canonical source: docs/02_documentation_language_policy.md`.

Japanese translations must not introduce requirements, ticket transitions, command contracts, gate criteria, schema fields, or acceptance rules that do not exist in the English canonical source.

## 4. Machine-readable identifiers remain English

The following values must remain English even inside translations or explanatory Japanese prose:

- Machine-readable keys and values.
- Command names, subcommands, flags, environment variables, and script names.
- Gate IDs, ticket IDs, run IDs, failure IDs, and report IDs.
- Crate names, binary names, module names, schema fields, and JSON/TOML/YAML keys.
- File names unless the file is an explicitly marked translation such as `*.ja.md`.

## 5. Handling currently canonical Japanese material

If a Japanese document is canonical or functions as the only source of operational truth, create or update an English canonical version before relying on it for loop execution. After the English source exists, mark the Japanese document as a translation, non-canonical explanation, or archive.

The migration order is:

1. Identify the operational claims in the Japanese document.
2. Create or update the English canonical source with those claims.
3. Add a `Canonical source:` pointer to the Japanese document.
4. Mark the Japanese document as `Status: translation`, `Status: non-canonical explanation`, or `Status: archived`.
5. Update references so tickets, gates, scripts, prompts, and schemas point to the English canonical source.

## 6. Prompts language rule

`prompts/` files are operational instructions for AI sessions and automation handoff. They must remain English by default. Japanese prompt translations may be added only as explicitly marked `*.ja.md` translations and must point back to the English canonical prompt.

## 7. Review checklist

Before accepting documentation or prompt changes, verify that:

- Canonical operational rules are written in English.
- Japanese files are marked as translations or non-canonical explanations.
- Machine-readable identifiers remain English.
- Any Japanese canonical source has an English canonical replacement before downstream tickets or gates rely on it.
