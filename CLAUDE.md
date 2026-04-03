# Knowledge Base - LLM Operation Rules

This is an LLM-driven markdown knowledge base. The LLM writes articles; the CLI handles hashing, indexing, compilation, and validation.

## Directory Structure

```
knowledge-base/
├── inbox/              # Drop zone. Put anything here.
├── sources/            # Immutable archive (CLI-managed, DO NOT modify)
├── wiki/               # Compiled articles (LLM writes these)
├── output/             # Generated artifacts (Q&A results, slides, etc.)
├── _manifest.json      # Source tracking (CLI-managed, DO NOT modify)
├── _index.json         # Article index (CLI-managed, DO NOT modify)
├── clipper-template.json  # Obsidian Web Clipper template (import this)
└── tools/kb.py         # CLI tool
```

## Ownership Rules

| Path | Owner | LLM may |
|------|-------|---------|
| `inbox/` | Human / Web Clipper | Read only (don't delete or move) |
| `sources/` | CLI (`kb ingest`) | Read only |
| `wiki/` | **LLM** (via `kb compile` or manual) | Read and Write |
| `output/` | **LLM** | Read and Write |
| `_manifest.json` | CLI | **Read only** |
| `_index.json` | CLI | **Read only** |

## Workflow

### One-Shot Sync (primary workflow)

```bash
kb sync    # = ingest + compile + index in one shot
```

This is the default workflow. It:
1. Processes all inbox/ files into sources/ (hash, dedup)
2. Auto-compiles pending sources into wiki articles (Claude API)
3. Rebuilds _index.json and reconciles manifest

### Watch Mode (hands-free)

```bash
kb watch   # Monitor inbox/ and auto-sync on new files
```

Runs `kb sync` automatically when new files appear in inbox/.
Ideal for use with Obsidian Web Clipper.

### Individual Commands

```bash
kb ingest   # Process inbox/ -> sources/ only
kb compile  # Compile pending sources -> wiki/ only
kb index    # Rebuild _index.json only
kb search <query>  # Search wiki/ articles
kb stats    # Show KB statistics + stale detection
kb health   # Run integrity checks
```

### Manual Article Writing

If you need to write or edit a wiki article manually (not via `kb compile`):

Create articles in `wiki/` with this exact frontmatter format:

```yaml
---
article_id: unique-kebab-case-slug
title: Human Readable Title
source_ids:
  - <source_id from manifest>
topics:
  - topic-name-kebab-case
summary: >
  2-3 sentence summary of the article content. This appears in _index.json
  and is used by LLMs for semantic search. Be specific about key concepts,
  entities, and conclusions.
created_at: "2026-04-04"
updated_at: "2026-04-04"
---

Article body in markdown...

## Related Articles
- [[other-article-id]] - brief description
```

**Rules for articles:**
- `article_id` must be unique across all articles
- `source_ids` must reference valid IDs from `_manifest.json`
- `topics` use kebab-case, lowercase (e.g., `machine-learning`, not `Machine Learning`)
- `summary` is critical for retrieval quality
- When updating an article, always update `updated_at`

### Q&A (when user asks a question about KB content)

1. Read `_index.json` to find relevant articles by scanning summaries and topics
2. Read the relevant wiki articles
3. Answer the question based on the article content
4. Optionally save the answer to `output/`

### Health Check

Run `kb health` periodically to catch:
- Missing source files
- Invalid frontmatter
- Index/wiki desync
- Orphaned files

## Obsidian Web Clipper Setup

1. Open `E:\Project\knowledge-base` as an Obsidian vault
2. Install Obsidian Web Clipper browser extension
3. Import `clipper-template.json` as a template in Web Clipper settings
4. Clip articles from Chrome -> they land in `inbox/`
5. Run `kb watch` to auto-process, or `kb sync` manually

## Cross-Project Access

This KB is accessible from other Claude Code projects as a global additional working directory.

**When accessing from other projects: READ-ONLY.**
- You may Read, Grep, and Glob files in this directory
- Do NOT write, edit, or create files here from other projects
- If you need to update the KB, tell the user to switch to the KB project

## Topic Naming Convention

Use kebab-case, lowercase. Normalize similar topics:
- `machine-learning` (not `ML`, `Machine Learning`, `machine_learning`)
- `prompt-engineering` (not `prompts`, `prompt-design`)
- When in doubt, check existing topics in `_index.json` before creating new ones
