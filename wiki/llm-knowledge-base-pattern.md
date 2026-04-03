---
article_id: llm-knowledge-base-pattern
title: LLM-Driven Knowledge Base Pattern
source_ids:
  - 16c0425f47df
topics:
  - llm-workflows
  - knowledge-management
  - personal-tools
summary: >
  Andrej Karpathy's approach to using LLMs as knowledge base compilers.
  Raw sources are ingested into a directory, LLMs compile them into a
  wiki of interlinked markdown articles, and the same LLMs perform Q&A
  against the wiki. Outputs feed back into the wiki, creating a
  self-reinforcing knowledge loop.
created_at: "2026-04-04"
updated_at: "2026-04-04"
---

# LLM-Driven Knowledge Base Pattern

A pattern for building personal knowledge bases where the LLM acts as both compiler and query engine.

## Core Loop

```
Sources (raw/) --> LLM Compile --> Wiki (md articles) --> Q&A --> Output --> Wiki (feedback)
```

## Key Components

### 1. Data Ingestion
- Source documents (articles, papers, repos, datasets, images) are collected into a raw directory
- Obsidian Web Clipper is useful for converting web articles to markdown
- Images should be downloaded locally for LLM reference

### 2. LLM Compilation
- The LLM incrementally "compiles" a wiki from raw sources
- Wiki = collection of interlinked .md files with:
  - Summaries of source data
  - Backlinks between articles
  - Concept categorization
- The LLM writes and maintains all wiki content; humans rarely edit directly

### 3. Q&A Against the Wiki
- At sufficient scale (~100 articles, ~400K words), complex questions can be answered
- LLM navigates via auto-maintained index files and summaries
- No RAG needed at this scale — summaries + index are sufficient

### 4. Output Formats
- Markdown documents
- Slide shows (Marp format)
- Matplotlib visualizations
- All viewable in Obsidian
- Outputs are "filed" back into the wiki, creating a feedback loop

### 5. Linting / Health Checks
- LLM-driven integrity checks over the wiki
- Finds inconsistencies, imputes missing data, suggests new connections
- Incrementally improves data quality

## Scale Considerations
- Works well at small-to-medium scale (~100-500 articles)
- At larger scale, consider synthetic data generation + fine-tuning
- RAG may become necessary beyond the LLM's effective context management

## Related Articles
- (none yet)
