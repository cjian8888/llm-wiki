# Contributing

Thank you for contributing to LLM Wiki.

## Before You Start

- Read `README.md` and `README.zh-CN.md` for project context.
- Review `docs/karpathy_design_pattern.md` before changing ingest, lint, or global knowledge-structure behavior.
- Keep changes local-first and consistent with the current LM Studio + Docker workflow unless the change explicitly updates runtime assumptions.

## Development Principles

- Prefer small, focused pull requests.
- Do not commit secrets such as `.env` or API keys.
- Keep generated examples and documentation aligned with the actual codebase.
- If you change user-facing behavior, update the relevant docs in the same PR.

## Documentation Sync Requirements

When the project evolves, contributors should keep these materials in sync when relevant:

- `README.md`
- `README.zh-CN.md`
- `ROADMAP.md`
- `.github/ISSUE_TEMPLATE/*`
- `.github/pull_request_template.md`

Examples:
- New capability added → update README and roadmap
- Workflow changed → update both language READMEs and PR template checklist if needed
- Scope or priorities changed → update roadmap and issue templates if reporting categories changed

## Pull Request Checklist

Before opening a PR, confirm:

- [ ] The change matches the LLM Wiki project direction
- [ ] Docs were updated if behavior, scope, or setup changed
- [ ] No secrets or local-only credentials were committed
- [ ] The change was tested at the appropriate level for its scope
- [ ] Generated outputs included in the repo still reflect current behavior

## Reporting Bugs and Ideas

- Use the bug report template for runtime, ingest, or documentation defects.
- Use the feature request template for roadmap proposals, workflow improvements, or new wiki capabilities.

## Code of Collaboration

Be concrete, keep scope tight, and optimize for a repo that stays understandable as it grows.
