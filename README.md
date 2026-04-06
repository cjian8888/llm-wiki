# LLM Wiki

A personal knowledge base following Karpathy's LLM Wiki pattern.

## Directory Structure

| Directory | Purpose |
|-----------|---------|
| `inbox/` | Drop new source documents here before ingestion |
| `wiki_nodes/` | LLM-generated wiki pages (summaries, entities, concepts) |
| `assets/` | Images and other media referenced by wiki pages |
| `scripts/` | Helper scripts for ingest, lint, and search operations |
| `docs/` | Project documentation and architectural specs |

## Key Files

- `CLAUDE.md` — Instructions for the LLM agent
- `wiki_nodes/index.md` — Content catalog of all wiki pages (created on first ingest)
- `wiki_nodes/log.md` — Append-only operation log (created on first ingest)

## Workflow

1. **Ingest**: Drop a source into `inbox/`, then ask the LLM to process it
2. **Query**: Ask questions; the LLM reads the wiki and synthesizes answers
3. **Lint**: Periodically ask the LLM to health-check the wiki for gaps and contradictions
