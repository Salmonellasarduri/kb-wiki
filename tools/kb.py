#!/usr/bin/env python3
"""kb - LLM-driven Knowledge Base CLI.

Deterministic tooling for an LLM-operated markdown knowledge base.
The LLM writes wiki articles; this CLI handles hashing, indexing, and validation.

Commands:
    ingest   - Process inbox/ files into sources/ with dedup
    compile  - Auto-generate wiki articles from pending sources via Claude API
    index    - Rebuild _index.json from wiki/ and reconcile manifest
    sync     - Run ingest + compile + index in one shot
    watch    - Monitor inbox/ for new files and auto-sync
    search   - Search wiki/ articles (ripgrep or fallback)
    stats    - Show knowledge base statistics
    health   - Run integrity checks
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KB_ROOT = Path(__file__).resolve().parent.parent
INBOX_DIR = KB_ROOT / "inbox"
SOURCES_DIR = KB_ROOT / "sources"
WIKI_DIR = KB_ROOT / "wiki"
OUTPUT_DIR = KB_ROOT / "output"
MANIFEST_PATH = KB_ROOT / "_manifest.json"
INDEX_PATH = KB_ROOT / "_index.json"

HASH_DISPLAY_LEN = 12  # chars used in filenames
MANIFEST_VERSION = 1
INDEX_VERSION = 1

# Frontmatter: must start at very beginning of file
FRONTMATTER_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*\n", re.DOTALL)

# Required frontmatter fields and their types
FRONTMATTER_SCHEMA = {
    "article_id": str,
    "title": str,
    "source_ids": list,
    "topics": list,
    "summary": str,
    "created_at": str,
    "updated_at": str,
}

COMPILE_MODEL = "claude-sonnet-4-20250514"
WATCH_DEBOUNCE_SEC = 3.0
MAX_SOURCE_BYTES = 200_000  # ~200KB, well within Claude's context window


# ---------------------------------------------------------------------------
# Atomic I/O
# ---------------------------------------------------------------------------

def atomic_write_json(path: Path, data: dict) -> None:
    """Write JSON atomically: write to temp file, fsync, then rename."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_json(path: Path) -> dict:
    """Load a JSON file, returning empty structure if missing or corrupt."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"WARNING: corrupt JSON at {path}: {e}", file=sys.stderr)
        return {}


def to_posix(path: Path, base: Path) -> str:
    """Convert a path to POSIX-style relative string for JSON storage."""
    return path.relative_to(base).as_posix()


# ---------------------------------------------------------------------------
# Frontmatter parsing (PyYAML)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> dict | None:
    """Parse YAML frontmatter from markdown text.

    Returns None if no frontmatter found.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None

    raw = m.group(1)
    try:
        result = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None

    if not isinstance(result, dict):
        return None

    # Ensure list fields are lists (YAML may parse single-item as string)
    for key in ("source_ids", "topics"):
        if key in result and isinstance(result[key], str):
            result[key] = [result[key]]

    # Ensure string fields are strings (YAML may parse dates as date objects)
    for key in ("created_at", "updated_at", "article_id", "title", "summary"):
        if key in result and not isinstance(result[key], str):
            result[key] = str(result[key])

    return result


def validate_frontmatter(fm: dict, path: Path) -> list[str]:
    """Validate frontmatter against schema. Returns list of error messages."""
    errors = []
    for field, expected_type in FRONTMATTER_SCHEMA.items():
        if field not in fm:
            errors.append(f"{path.name}: missing required field '{field}'")
        elif not isinstance(fm[field], expected_type):
            errors.append(
                f"{path.name}: field '{field}' expected {expected_type.__name__}, "
                f"got {type(fm[field]).__name__}"
            )
    return errors


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def file_hash(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sanitize_filename(name: str) -> str:
    """Sanitize a filename for safe filesystem use."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    if len(name) > 80:
        stem, ext = os.path.splitext(name)
        name = stem[:80] + ext
    return name


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_ingest(_args: argparse.Namespace) -> int:
    """Process inbox/ files: hash, dedup, copy to sources/, update manifest."""
    manifest = load_json(MANIFEST_PATH)
    if not manifest:
        manifest = {"version": MANIFEST_VERSION, "_hash_index": {}, "items": {}}

    hash_index: dict = manifest.setdefault("_hash_index", {})
    items: dict = manifest.setdefault("items", {})

    inbox_files = [
        f for f in INBOX_DIR.iterdir()
        if f.is_file() and f.name != ".gitkeep"
    ]

    if not inbox_files:
        print("inbox/ is empty. Nothing to ingest.")
        return 0

    ingested = 0
    skipped_dup = 0
    errors = 0
    to_delete: list[Path] = []
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for fpath in sorted(inbox_files):
        try:
            fhash = file_hash(fpath)
        except OSError as e:
            print(f"ERROR: cannot read {fpath.name}: {e}")
            errors += 1
            continue

        if fhash in hash_index:
            existing_id = hash_index[fhash]
            print(f"SKIP (duplicate): {fpath.name} -> existing {existing_id}")
            skipped_dup += 1
            to_delete.append(fpath)
            continue

        source_id = fhash[:HASH_DISPLAY_LEN]
        while source_id in items and items[source_id]["hash"] != fhash:
            if len(source_id) >= len(fhash):
                print(f"ERROR: hash collision or corrupt manifest for {fpath.name}")
                errors += 1
                break
            source_id = fhash[:len(source_id) + 1]
        else:
            pass  # no collision, proceed
        if len(source_id) >= len(fhash) and source_id in items:
            continue

        safe_name = sanitize_filename(fpath.name)
        dest_name = f"{source_id}_{safe_name}"
        dest_path = SOURCES_DIR / dest_name
        meta_path = SOURCES_DIR / f"{source_id}_meta.json"

        try:
            shutil.copy2(fpath, dest_path)
        except OSError as e:
            print(f"ERROR: copy failed for {fpath.name}: {e}")
            errors += 1
            continue

        meta = {
            "source_id": source_id,
            "hash": fhash,
            "original_name": fpath.name,
            "ingested_at": now,
        }
        atomic_write_json(meta_path, meta)

        hash_index[fhash] = source_id
        items[source_id] = {
            "hash": fhash,
            "original_name": fpath.name,
            "source_path": to_posix(dest_path, KB_ROOT),
            "meta_path": to_posix(meta_path, KB_ROOT),
            "status": "pending",
            "ingested_at": now,
            "compiled_at": None,
            "article_ids": [],
            "error": None,
        }

        to_delete.append(fpath)
        ingested += 1
        print(f"INGESTED: {fpath.name} -> {source_id}")

    atomic_write_json(MANIFEST_PATH, manifest)

    for fpath in to_delete:
        try:
            fpath.unlink()
        except OSError:
            pass

    print(f"\nDone: {ingested} ingested, {skipped_dup} duplicates skipped, {errors} errors")
    return 2 if errors else 0


def cmd_compile(_args: argparse.Namespace) -> int:
    """Compile pending sources into wiki articles using Claude API."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        return 2

    manifest = load_json(MANIFEST_PATH)
    if not manifest or "items" not in manifest:
        print("No manifest found. Run 'kb ingest' first.")
        return 1

    items = manifest["items"]
    index = load_json(INDEX_PATH)

    # Find pending or failed sources
    pending = {
        sid: item for sid, item in items.items()
        if item.get("status") in ("pending", "failed", "compiling")
    }

    if not pending:
        print("No pending sources to compile.")
        return 0

    # Build existing articles context
    existing_articles = index.get("articles", [])
    existing_ctx = "\n".join(
        f"- {a['title']} (topics: {', '.join(a['topics'])}): {a['summary']}"
        for a in existing_articles
    ) or "(none yet)"

    client = anthropic.Anthropic()
    today = datetime.date.today().isoformat()
    compiled = 0
    failed = 0

    for sid, item in pending.items():
        source_path = KB_ROOT / item["source_path"]
        if not source_path.resolve().is_relative_to(KB_ROOT.resolve()):
            print(f"ERROR: source_path escapes KB root: {item['source_path']}")
            item["status"] = "failed"
            item["error"] = "path traversal in source_path"
            failed += 1
            continue
        if not source_path.exists():
            print(f"ERROR: source file missing: {item['source_path']}")
            item["status"] = "failed"
            item["error"] = "source file missing"
            failed += 1
            continue

        # Guard against oversized sources
        source_size = source_path.stat().st_size
        if source_size > MAX_SOURCE_BYTES:
            print(f"ERROR: source too large ({source_size} bytes): {source_path.name}")
            item["status"] = "failed"
            item["error"] = f"source too large: {source_size} bytes"
            failed += 1
            continue

        try:
            source_text = source_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"ERROR: cannot read {source_path.name}: {e}")
            item["status"] = "failed"
            item["error"] = str(e)
            failed += 1
            continue

        # Mark as compiling
        item["status"] = "compiling"
        atomic_write_json(MANIFEST_PATH, manifest)

        print(f"COMPILING: {item['original_name']} ({sid})...")

        prompt = f"""Read this source document and compile it into a wiki article.

Source document (source_id: {sid}):
---
{source_text}
---

Existing articles in the wiki (avoid duplication, add cross-references where relevant):
{existing_ctx}

Write a complete wiki article in markdown with this EXACT frontmatter format at the very beginning:
---
article_id: unique-kebab-case-slug
title: Human Readable Title
source_ids:
  - {sid}
topics:
  - relevant-topic-kebab-case
summary: >
  2-3 sentence summary of the key concepts and conclusions.
  Be specific about entities, terminology, and actionable insights.
created_at: "{today}"
updated_at: "{today}"
---

Rules:
- article_id must be unique, descriptive, kebab-case
- topics must be kebab-case, lowercase
- summary is critical for retrieval quality
- Include a "## Related Articles" section at the end with [[article-id]] links if relevant
- Write in the language of the source document
- Focus on extracting key concepts, patterns, and actionable knowledge"""

        article_text = None
        fm: dict | None = None
        for attempt in range(2):
            try:
                response = client.messages.create(
                    model=COMPILE_MODEL,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                )
                candidate = response.content[0].text  # type: ignore[union-attr]

                # Strip markdown code fences if the model wrapped the output
                candidate = re.sub(r"\A\s*```(?:markdown|md)?\s*\n", "", candidate)
                candidate = re.sub(r"\n```\s*\Z", "", candidate)

                fm = parse_frontmatter(candidate)
                if fm is None:
                    if attempt == 0:
                        prompt += "\n\nIMPORTANT: Your previous response did not have valid YAML frontmatter. The article MUST start with --- on the very first line, followed by YAML fields, then --- to close."
                        print(f"  Retry (invalid frontmatter)...")
                        continue
                    else:
                        raise ValueError("No valid frontmatter after retry")

                errors = validate_frontmatter(fm, Path(fm.get("article_id", "unknown")))
                if errors:
                    if attempt == 0:
                        prompt += f"\n\nIMPORTANT: Frontmatter validation failed: {'; '.join(errors)}. Fix these issues."
                        print(f"  Retry (validation: {errors[0]})...")
                        continue
                    else:
                        raise ValueError(f"Frontmatter validation failed: {'; '.join(errors)}")

                article_text = candidate
                break

            except Exception as e:
                if attempt == 0 and "frontmatter" in str(e).lower():
                    continue
                print(f"  ERROR: {e}")
                item["status"] = "failed"
                item["error"] = str(e)[:200]
                failed += 1
                break

        if article_text is None or fm is None:
            if item["status"] != "failed":
                item["status"] = "failed"
                item["error"] = "compile failed after retries"
                failed += 1
            continue

        # Write wiki article (with path traversal guard)
        article_id: str = fm["article_id"]
        if "/" in article_id or "\\" in article_id or ".." in article_id:
            print(f"  ERROR: article_id contains invalid characters: {article_id!r}")
            item["status"] = "failed"
            item["error"] = f"unsafe article_id: {article_id!r}"
            failed += 1
            continue
        wiki_path = WIKI_DIR / f"{article_id}.md"
        if not wiki_path.resolve().is_relative_to(WIKI_DIR.resolve()):
            print(f"  ERROR: article_id resolves outside wiki/: {article_id!r}")
            item["status"] = "failed"
            item["error"] = f"path traversal in article_id: {article_id!r}"
            failed += 1
            continue
        wiki_path.write_text(article_text, encoding="utf-8")

        item["status"] = "compiled"
        item["compiled_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        item["article_ids"] = [article_id]
        item["error"] = None
        compiled += 1

        print(f"  -> wiki/{article_id}.md")

        # Update existing context for next source
        existing_ctx += f"\n- {fm['title']} (topics: {', '.join(fm.get('topics', []))}): {fm.get('summary', '')}"

    atomic_write_json(MANIFEST_PATH, manifest)
    print(f"\nDone: {compiled} compiled, {failed} failed")
    return 2 if failed else 0


def cmd_index(_args: argparse.Namespace) -> int:
    """Rebuild _index.json from wiki/ and reconcile manifest status."""
    wiki_files = sorted(WIKI_DIR.glob("*.md"))
    if not wiki_files:
        index_data = {
            "version": INDEX_VERSION,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "article_count": 0,
            "articles": [],
        }
        atomic_write_json(INDEX_PATH, index_data)
        print("wiki/ is empty. Index cleared.")
        return 0

    articles = []
    all_errors = []
    seen_ids = {}
    source_to_articles: dict[str, list[str]] = {}

    for wf in wiki_files:
        try:
            text = wf.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            all_errors.append(f"{wf.name}: cannot read file: {e}")
            continue

        fm = parse_frontmatter(text)

        if fm is None:
            all_errors.append(f"{wf.name}: no frontmatter found")
            continue

        errors = validate_frontmatter(fm, wf)
        if errors:
            all_errors.extend(errors)
            continue

        aid = fm["article_id"]
        if aid in seen_ids:
            all_errors.append(
                f"{wf.name}: duplicate article_id '{aid}' (also in {seen_ids[aid]})"
            )
            continue
        seen_ids[aid] = wf.name

        article_entry = {
            "id": aid,
            "path": to_posix(wf, KB_ROOT),
            "title": fm["title"],
            "summary": fm["summary"],
            "topics": fm["topics"],
            "source_ids": fm["source_ids"],
            "created_at": fm["created_at"],
            "updated_at": fm["updated_at"],
        }
        articles.append(article_entry)

        for sid in fm["source_ids"]:
            source_to_articles.setdefault(sid, []).append(aid)

    # Write index
    index_data = {
        "version": INDEX_VERSION,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "article_count": len(articles),
        "articles": articles,
    }
    atomic_write_json(INDEX_PATH, index_data)

    # Reconcile manifest
    manifest = load_json(MANIFEST_PATH)
    if manifest and "items" in manifest:
        changed = False
        reconciled = 0
        for sid, item in manifest["items"].items():
            if sid in source_to_articles:
                if item["status"] in ("pending", "compiling", "failed"):
                    item["status"] = "compiled"
                    item["compiled_at"] = datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat()
                    reconciled += 1
                    changed = True
                if item.get("article_ids") != source_to_articles[sid]:
                    item["article_ids"] = source_to_articles[sid]
                    changed = True
            elif item.get("article_ids"):
                item["article_ids"] = []
                changed = True
        if changed:
            atomic_write_json(MANIFEST_PATH, manifest)
        if reconciled:
            print(f"Manifest reconciled: {reconciled} sources marked compiled")

    topics = set()
    for a in articles:
        topics.update(a["topics"])

    print(f"Indexed: {len(articles)} articles, {len(topics)} topics")
    if all_errors:
        print(f"\nWarnings ({len(all_errors)}):")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    return 0


def cmd_sync(_args: argparse.Namespace) -> int:
    """Run ingest + compile + index in one shot."""
    print("=== INGEST ===")
    rc = cmd_ingest(_args)
    if rc == 2:
        print("\nIngest had errors. Continuing anyway...")

    print("\n=== COMPILE ===")
    rc_compile = cmd_compile(_args)

    print("\n=== INDEX ===")
    rc_index = cmd_index(_args)

    # Quick health summary
    print("\n=== HEALTH ===")
    # Inline minimal health check
    manifest = load_json(MANIFEST_PATH)
    items = manifest.get("items", {})
    pending = sum(1 for v in items.values() if v.get("status") == "pending")
    failed_count = sum(1 for v in items.values() if v.get("status") == "failed")
    compiled = sum(1 for v in items.values() if v.get("status") == "compiled")
    print(f"Sources: {compiled} compiled, {pending} pending, {failed_count} failed")

    index = load_json(INDEX_PATH)
    print(f"Articles: {index.get('article_count', 0)}")

    if rc_compile == 2 or rc_index == 2:
        return 2
    if rc_compile == 1 or rc_index == 1:
        return 1
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    """Watch inbox/ for new files and auto-sync on changes."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("ERROR: watchdog package not installed. Run: pip install watchdog")
        return 2

    class InboxHandler(FileSystemEventHandler):
        def __init__(self):
            self.pending = False
            self.last_event = 0.0

        def on_created(self, event):
            if not event.is_directory and not event.src_path.endswith(".gitkeep"):
                self.pending = True
                self.last_event = time.time()
                print(f"  Detected: {Path(event.src_path).name}")

        def on_modified(self, event):
            if not event.is_directory and not event.src_path.endswith(".gitkeep"):
                self.pending = True
                self.last_event = time.time()

    handler = InboxHandler()
    observer = Observer()
    observer.schedule(handler, str(INBOX_DIR), recursive=False)
    observer.start()

    print(f"Watching {INBOX_DIR} for new files... (Ctrl+C to stop)")
    print(f"Debounce: {WATCH_DEBOUNCE_SEC}s after last file event")

    try:
        while True:
            time.sleep(0.5)
            if handler.pending and (time.time() - handler.last_event) >= WATCH_DEBOUNCE_SEC:
                handler.pending = False
                print(f"\n{'='*50}")
                print(f"New files detected. Running sync...")
                print(f"{'='*50}\n")
                cmd_sync(args)
                print(f"\nWatching {INBOX_DIR}... (Ctrl+C to stop)")
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()
    observer.join()
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Search wiki/ articles using ripgrep or Python fallback."""
    query = args.query

    rg = shutil.which("rg")
    if rg:
        cmd = [
            rg, "--color=never", "-n", "-i",
            "--fixed-strings",
            "--glob", "*.md",
            "--", query,
            str(WIKI_DIR),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            return 0
        elif result.returncode == 1:
            print("No matches found.")
            return 0
        else:
            print(f"rg error: {result.stderr}")
            return 2
    else:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        found = False
        for wf in sorted(WIKI_DIR.glob("*.md")):
            try:
                lines = wf.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    print(f"{wf.name}:{i}:{line}")
                    found = True
        if not found:
            print("No matches found.")
        return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show knowledge base statistics including stale article detection."""
    manifest = load_json(MANIFEST_PATH)
    index = load_json(INDEX_PATH)

    items = manifest.get("items", {})
    inbox_count = sum(1 for f in INBOX_DIR.iterdir() if f.is_file() and f.name != ".gitkeep")
    source_count = len(items)
    pending = sum(1 for v in items.values() if v.get("status") == "pending")
    failed = sum(1 for v in items.values() if v.get("status") == "failed")
    compiled = sum(1 for v in items.values() if v.get("status") == "compiled")
    article_count = index.get("article_count", 0)
    last_indexed = index.get("generated_at", "never")

    articles = index.get("articles", [])
    topics = sorted(set(t for a in articles for t in a.get("topics", [])))

    # Stale article detection: check if wiki file mtime > updated_at
    stale_articles = []
    for a in articles:
        wiki_path = KB_ROOT / a["path"]
        if wiki_path.exists():
            mtime = datetime.datetime.fromtimestamp(
                wiki_path.stat().st_mtime, tz=datetime.timezone.utc
            )
            try:
                updated = datetime.datetime.fromisoformat(a["updated_at"])
                if not updated.tzinfo:
                    updated = updated.replace(tzinfo=datetime.timezone.utc)
            except (ValueError, TypeError):
                continue
            # If file was modified more than 1 day after updated_at, it's stale
            if mtime > updated + datetime.timedelta(days=1):
                stale_articles.append(a["title"])

    # Also check for sources that were re-ingested after article was compiled
    recompile_needed = []
    for sid, item in items.items():
        if item.get("status") == "compiled" and item.get("compiled_at") and item.get("ingested_at"):
            try:
                ingested = datetime.datetime.fromisoformat(item["ingested_at"])
                compiled_dt = datetime.datetime.fromisoformat(item["compiled_at"])
                if ingested > compiled_dt:
                    recompile_needed.append(item.get("original_name", sid))
            except (ValueError, TypeError):
                continue

    data = {
        "inbox": inbox_count,
        "sources": {"total": source_count, "pending": pending, "compiled": compiled, "failed": failed},
        "articles": article_count,
        "topics": topics,
        "last_indexed": last_indexed,
        "stale_articles": stale_articles,
        "recompile_needed": recompile_needed,
    }

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("=== Knowledge Base Stats ===")
        print(f"Inbox:       {inbox_count} files waiting")
        print(f"Sources:     {source_count} total ({pending} pending, {compiled} compiled, {failed} failed)")
        print(f"Wiki:        {article_count} articles")
        print(f"Topics:      {len(topics)}")
        if topics:
            print(f"             {', '.join(topics)}")
        print(f"Last index:  {last_indexed}")
        if stale_articles:
            print(f"\nStale articles ({len(stale_articles)}):")
            for t in stale_articles:
                print(f"  - {t}")
        if recompile_needed:
            print(f"\nRecompile needed ({len(recompile_needed)}):")
            for n in recompile_needed:
                print(f"  - {n}")

    return 0


def cmd_health(args: argparse.Namespace) -> int:
    """Run integrity checks on the knowledge base."""
    manifest = load_json(MANIFEST_PATH)
    index = load_json(INDEX_PATH)
    issues = []

    items = manifest.get("items", {})
    hash_index = manifest.get("_hash_index", {})

    # 1. Check all manifest source_paths exist
    for sid, item in items.items():
        source_path = item.get("source_path", "")
        sp = KB_ROOT / source_path if source_path else None
        if not sp or not sp.exists():
            issues.append(("ERROR", f"source missing: {source_path or '(no path)'} (id={sid})"))
        meta_path = item.get("meta_path", "")
        mp = KB_ROOT / meta_path if meta_path else None
        if not mp or not mp.exists():
            issues.append(("WARN", f"sidecar missing: {meta_path or '(no path)'} (id={sid})"))

    # 2. Check hash_index consistency
    for _fhash, sid in hash_index.items():
        if sid not in items:
            issues.append(("ERROR", f"hash_index references missing item: {sid}"))

    # 3. Validate wiki articles
    wiki_files = list(WIKI_DIR.glob("*.md"))
    seen_ids = {}
    for wf in wiki_files:
        try:
            text = wf.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            issues.append(("ERROR", f"wiki/{wf.name}: cannot read: {e}"))
            continue
        fm = parse_frontmatter(text)
        if fm is None:
            issues.append(("ERROR", f"wiki/{wf.name}: no frontmatter"))
            continue
        errs = validate_frontmatter(fm, wf)
        for e in errs:
            issues.append(("ERROR", e))
        if "article_id" in fm:
            aid = fm["article_id"]
            if aid in seen_ids:
                issues.append(("ERROR", f"duplicate article_id '{aid}': {wf.name} and {seen_ids[aid]}"))
            seen_ids[aid] = wf.name
            for sid in fm.get("source_ids", []):
                if sid not in items:
                    issues.append(("WARN", f"wiki/{wf.name}: source_id '{sid}' not in manifest"))

    # 4. Check index matches wiki
    indexed_paths = {a["path"] for a in index.get("articles", [])}
    actual_paths = {to_posix(wf, KB_ROOT) for wf in wiki_files}
    for missing in actual_paths - indexed_paths:
        issues.append(("WARN", f"wiki article not in index: {missing}"))
    for stale in indexed_paths - actual_paths:
        issues.append(("WARN", f"index references missing article: {stale}"))

    # 5. Check for orphaned source files
    manifest_sources = {item.get("source_path", "") for item in items.values()}
    manifest_metas = {item.get("meta_path", "") for item in items.values()}
    for sf in SOURCES_DIR.iterdir():
        if sf.name == ".gitkeep":
            continue
        rel = to_posix(sf, KB_ROOT)
        if rel not in manifest_sources and rel not in manifest_metas:
            issues.append(("WARN", f"orphaned file in sources/: {sf.name}"))

    # Report
    if not issues:
        print("Health check passed. No issues found.")
        return 0

    error_list = [i for i in issues if i[0] == "ERROR"]
    warn_list = [i for i in issues if i[0] == "WARN"]

    if args.json:
        print(json.dumps({
            "errors": len(error_list),
            "warnings": len(warn_list),
            "issues": [{"severity": s, "message": m} for s, m in issues],
        }, indent=2, ensure_ascii=False))
    else:
        print(f"Health check: {len(error_list)} errors, {len(warn_list)} warnings\n")
        for severity, msg in issues:
            print(f"  [{severity}] {msg}")

    return 1 if error_list else 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="kb",
        description="LLM-driven Knowledge Base CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ingest
    sub.add_parser("ingest", help="Process inbox/ into sources/")

    # compile
    sub.add_parser("compile", help="Auto-generate wiki articles from pending sources")

    # index
    sub.add_parser("index", help="Rebuild _index.json from wiki/")

    # sync
    sub.add_parser("sync", help="Run ingest + compile + index")

    # watch
    sub.add_parser("watch", help="Monitor inbox/ and auto-sync on new files")

    # search
    p_search = sub.add_parser("search", help="Search wiki/ articles")
    p_search.add_argument("query", help="Search query")

    # stats
    p_stats = sub.add_parser("stats", help="Show KB statistics")
    p_stats.add_argument("--json", action="store_true", help="Machine-readable output")

    # health
    p_health = sub.add_parser("health", help="Run integrity checks")
    p_health.add_argument("--json", action="store_true", help="Machine-readable output")

    args = parser.parse_args()

    # Ensure directories exist
    for d in (INBOX_DIR, SOURCES_DIR, WIKI_DIR, OUTPUT_DIR):
        d.mkdir(parents=True, exist_ok=True)

    commands = {
        "ingest": cmd_ingest,
        "compile": cmd_compile,
        "index": cmd_index,
        "sync": cmd_sync,
        "watch": cmd_watch,
        "search": cmd_search,
        "stats": cmd_stats,
        "health": cmd_health,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
