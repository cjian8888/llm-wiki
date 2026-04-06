# LLM Wiki

A local-first, continuously evolving knowledge base built around Karpathy’s LLM Wiki pattern.

Instead of treating documents as files to search over and re-interpret every time, this project treats ingestion as compilation: each new source is transformed into structured wiki nodes that can accumulate, interlink, and improve over time.

## Highlights

- Local-first ingestion with LM Studio
- Automatic inbox watcher powered by `watchdog`
- OpenAI-compatible model interface
- Structured Markdown output with YAML frontmatter
- Obsidian-friendly knowledge storage under `wiki_nodes/`
- Source archiving after successful ingest
- Startup backlog scan plus live file watching

## Architecture

The system is split into three layers:

1. **Infrastructure layer**
   - Docker / Docker Compose
   - `scripts/daemon.py`
   - `watchdog` file event monitoring

2. **Capability layer**
   - `scripts/lib/loader.py` — source loading
   - `scripts/lib/llm_client.py` — model calls via OpenAI-compatible API
   - `scripts/ingest.py` — orchestration, rendering, and archiving

3. **Knowledge layer**
   - `wiki_nodes/source_summary/*.md`
   - YAML frontmatter for metadata
   - Markdown body for summary, claims, entities, and concepts

## Repository Layout

```text
.
├── assets/                   # Images and supporting media
├── docs/                     # Design docs and implementation blueprint
├── inbox/                    # Drop source files here for ingestion
│   └── archived/             # Successfully ingested source files
├── scripts/
│   ├── daemon.py             # Long-running inbox watcher
│   ├── ingest.py             # End-to-end ingest pipeline
│   └── lib/
│       ├── llm_client.py     # OpenAI-compatible LLM client
│       └── loader.py         # Source document loader
├── wiki_nodes/
│   └── source_summary/       # Generated wiki nodes
├── CLAUDE.md                 # Minimal project memory pointer
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## How It Works

1. Put a `.md` or `.txt` file into `inbox/`
2. The daemon detects new files, or processes existing backlog files on startup
3. The ingest pipeline loads the document text
4. The configured model extracts:
   - summary
   - key claims
   - entities
   - concepts
5. A wiki node is written to `wiki_nodes/source_summary/`
6. The original source is moved to `inbox/archived/`

## Current Runtime

This project is currently configured to use **LM Studio** as a local OpenAI-compatible backend.

Example `.env`:

```env
LLM_BASE_URL="http://host.docker.internal:1234/v1"
LLM_API_KEY="lm-studio"
LLM_MODEL_NAME="gemma-4-e4b-it"
```

Notes:
- LM Studio must have **Local Server** enabled
- The selected model must be loaded before ingestion
- Because the daemon runs in Docker, the container uses `host.docker.internal` instead of `localhost`

## Quick Start

### 1. Start LM Studio local server

In LM Studio:
- Open **Developer > Local Server**
- Load a model
- Confirm the OpenAI-compatible server is running

You can verify locally with:

```bash
curl http://localhost:1234/v1/models
```

### 2. Configure environment

Create `.env` from `.env.example`, then point it to your LM Studio server or another OpenAI-compatible backend.

### 3. Start the daemon

```bash
docker compose up --build -d
```

### 4. Drop a source file into `inbox/`

Example:

```bash
cp some-note.md inbox/
```

### 5. Inspect outputs

Generated wiki node:

```text
wiki_nodes/source_summary/<slug>.md
```

Archived source:

```text
inbox/archived/<original-file>
```

### 6. Stop the daemon

```bash
docker compose down
```

## Generated Node Format

Each generated node includes YAML frontmatter and structured sections:

```yaml
---
id: "example-slug"
title: "Example Slug"
type: source_summary
tags:
  - example
created: "2026-04-06"
updated: "2026-04-06"
source_file: "inbox/example.md"
source_count: 1
status: active
confidence: medium
related: []
---
```

Body sections:
- Summary
- Key claims
- Entities
- Core concepts
- Open questions / knowledge gaps
- References

## Status

Implemented:
- Containerized daemon runtime
- OpenAI-compatible LLM client
- Local LM Studio integration
- Startup backlog ingestion
- Live file-event ingestion
- Archive-on-success workflow

Planned:
- Lint / graph maintenance pass
- Automatic interlinking
- Contradiction detection across nodes
- Richer concept graph generation

## Development Notes

- Supported source formats: `.md`, `.txt`
- The daemon currently ingests files sequentially
- Successful ingestion depends on the configured model returning valid structured JSON
- Project instructions intentionally keep `CLAUDE.md` minimal and move architecture detail into `docs/`

## License

Currently unlicensed. Add a license before public distribution if needed.
