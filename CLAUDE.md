# Knowledge Base - LLM Operation Rules

This is an LLM-driven markdown knowledge base. The LLM writes articles; the CLI handles hashing, indexing, and validation.

## Directory Structure

```
knowledge-base/
├── inbox/           # Drop zone. Put anything here.
├── sources/         # Immutable archive (CLI-managed, DO NOT modify)
├── wiki/            # Compiled articles (LLM writes these)
├── output/          # Generated artifacts (Q&A results, slides, etc.)
├── _manifest.json   # Source tracking (CLI-managed, DO NOT modify)
├── _index.json      # Article index (CLI-managed, DO NOT modify)
└── tools/kb.py      # CLI tool
```

## Ownership Rules

| Path | Owner | LLM may |
|------|-------|---------|
| `inbox/` | Human | Read only (don't delete or move) |
| `sources/` | CLI (`kb ingest`) | Read only |
| `wiki/` | **LLM** | Read and Write |
| `output/` | **LLM** | Read and Write |
| `_manifest.json` | CLI (`kb ingest`, `kb index`) | **Read only** |
| `_index.json` | CLI (`kb index`) | **Read only** |

## Workflow

### Ingest + Compile (when user says "organize" / "compile" / "sync")

1. Run `python tools/kb.py ingest` to process inbox/ files
2. Run `python tools/kb.py stats` to see pending sources
3. Read `_manifest.json` and find items with `"status": "pending"`
4. For each pending source: read the source file, generate or update a wiki article
5. Run `python tools/kb.py index` to rebuild the index and reconcile manifest
6. Run `python tools/kb.py health` to verify integrity

### Writing Wiki Articles

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
- `summary` is critical for retrieval quality. Include key entities, terminology, and conclusions
- Multiple sources can feed into one article; one source can feed into multiple articles
- When updating an article, always update `updated_at`

### Q&A (when user asks a question about KB content)

1. Read `_index.json` to find relevant articles by scanning summaries and topics
2. Read the relevant wiki articles
3. Answer the question based on the article content
4. Optionally save the answer to `output/` if it's worth preserving

### Health Check

Run `python tools/kb.py health` periodically to catch:
- Missing source files
- Invalid frontmatter
- Index/wiki desync
- Orphaned files

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
