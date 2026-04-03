#!/usr/bin/env python3
"""kb - LLM-driven Knowledge Base CLI.

Deterministic tooling for an LLM-operated markdown knowledge base.
The LLM writes wiki articles; this CLI handles hashing, indexing, and validation.

Commands:
    ingest  - Process inbox/ files into sources/ with dedup
    index   - Rebuild _index.json from wiki/ and reconcile manifest
    search  - Search wiki/ articles (ripgrep or fallback)
    stats   - Show knowledge base statistics
    health  - Run integrity checks
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
from pathlib import Path

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

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

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


# ---------------------------------------------------------------------------
# Frontmatter parsing (no PyYAML dependency)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> dict | None:
    """Parse YAML-like frontmatter from markdown text.

    Handles simple key: value, key: [list], and multi-line summary (>).
    Returns None if no frontmatter found.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None

    raw = m.group(1)
    result = {}
    current_key = None
    multiline_buf = []

    for line in raw.split("\n"):
        # Continuation of multi-line value
        if current_key and (line.startswith("  ") or line.startswith("\t")):
            multiline_buf.append(line.strip())
            continue

        # Flush previous multi-line
        if current_key and multiline_buf:
            result[current_key] = " ".join(multiline_buf)
            current_key = None
            multiline_buf = []

        # Skip empty / comment lines
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # key: value
        colon_idx = stripped.find(":")
        if colon_idx < 0:
            continue

        key = stripped[:colon_idx].strip()
        val = stripped[colon_idx + 1:].strip()

        # Inline list: [a, b, c]
        if val.startswith("[") and val.endswith("]"):
            items = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
            result[key] = items
        # Multi-line indicator
        elif val == ">" or val == "|":
            current_key = key
            multiline_buf = []
        # List item start (next lines are - items)
        elif val == "":
            result[key] = val
        else:
            # Strip quotes
            result[key] = val.strip("'\"")

    # Flush final multi-line
    if current_key and multiline_buf:
        result[current_key] = " ".join(multiline_buf)

    # Handle YAML list items (- value) that follow a key with empty value
    # Re-parse for list detection
    lines = raw.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        colon_idx = stripped.find(":")
        if colon_idx >= 0:
            key = stripped[:colon_idx].strip()
            val = stripped[colon_idx + 1:].strip()
            if val == "" and i + 1 < len(lines) and lines[i + 1].strip().startswith("- "):
                items = []
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith("- "):
                    items.append(lines[j].strip()[2:].strip().strip("'\""))
                    j += 1
                result[key] = items
                i = j
                continue
        i += 1

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
    # Check article_id uniqueness is done at index level
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
    # Remove path separators and problematic chars
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    # Truncate to reasonable length
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
    to_delete: list[Path] = []  # defer inbox deletion until after manifest write
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for fpath in sorted(inbox_files):
        try:
            fhash = file_hash(fpath)
        except OSError as e:
            print(f"ERROR: cannot read {fpath.name}: {e}")
            errors += 1
            continue

        # Dedup check via hash index
        if fhash in hash_index:
            existing_id = hash_index[fhash]
            print(f"SKIP (duplicate): {fpath.name} -> existing {existing_id}")
            skipped_dup += 1
            to_delete.append(fpath)
            continue

        # Generate source ID from hash
        source_id = fhash[:HASH_DISPLAY_LEN]
        # Handle rare collision in display ID
        while source_id in items and items[source_id]["hash"] != fhash:
            source_id = fhash[:len(source_id) + 1]

        safe_name = sanitize_filename(fpath.name)
        dest_name = f"{source_id}_{safe_name}"
        dest_path = SOURCES_DIR / dest_name
        meta_path = SOURCES_DIR / f"{source_id}_meta.json"

        # Copy to sources/
        try:
            shutil.copy2(fpath, dest_path)
        except OSError as e:
            print(f"ERROR: copy failed for {fpath.name}: {e}")
            errors += 1
            continue

        # Write sidecar metadata
        meta = {
            "source_id": source_id,
            "hash": fhash,
            "original_name": fpath.name,
            "ingested_at": now,
        }
        atomic_write_json(meta_path, meta)

        # Update manifest in memory
        hash_index[fhash] = source_id
        items[source_id] = {
            "hash": fhash,
            "original_name": fpath.name,
            "source_path": str(dest_path.relative_to(KB_ROOT)),
            "meta_path": str(meta_path.relative_to(KB_ROOT)),
            "status": "pending",
            "ingested_at": now,
            "compiled_at": None,
            "article_ids": [],
            "error": None,
        }

        to_delete.append(fpath)
        ingested += 1
        print(f"INGESTED: {fpath.name} -> {source_id}")

    # Write manifest FIRST, then delete inbox files (transaction safety)
    atomic_write_json(MANIFEST_PATH, manifest)

    for fpath in to_delete:
        try:
            fpath.unlink()
        except OSError:
            pass  # non-fatal: will be deduped on next ingest

    print(f"\nDone: {ingested} ingested, {skipped_dup} duplicates skipped, {errors} errors")
    return 2 if errors else 0


def cmd_index(_args: argparse.Namespace) -> int:
    """Rebuild _index.json from wiki/ and reconcile manifest status."""
    wiki_files = sorted(WIKI_DIR.glob("*.md"))
    if not wiki_files:
        # Write empty index
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
            "path": str(wf.relative_to(KB_ROOT)),
            "title": fm["title"],
            "summary": fm["summary"],
            "topics": fm["topics"],
            "source_ids": fm["source_ids"],
            "created_at": fm["created_at"],
            "updated_at": fm["updated_at"],
        }
        articles.append(article_entry)

        # Track source->article mapping for manifest reconciliation
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

    # Reconcile manifest: update status and article_ids based on wiki source_ids
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
                # Source no longer referenced by any article
                item["article_ids"] = []
                changed = True
        if changed:
            atomic_write_json(MANIFEST_PATH, manifest)
        if reconciled:
            print(f"Manifest reconciled: {reconciled} sources marked compiled")

    # Report
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


def cmd_search(args: argparse.Namespace) -> int:
    """Search wiki/ articles using ripgrep or Python fallback."""
    query = args.query

    # Try ripgrep first
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
        # Python fallback
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
    """Show knowledge base statistics."""
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

    data = {
        "inbox": inbox_count,
        "sources": {"total": source_count, "pending": pending, "compiled": compiled, "failed": failed},
        "articles": article_count,
        "topics": topics,
        "last_indexed": last_indexed,
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
            # Check source_ids exist in manifest
            for sid in fm.get("source_ids", []):
                if sid not in items:
                    issues.append(("WARN", f"wiki/{wf.name}: source_id '{sid}' not in manifest"))

    # 4. Check index matches wiki
    indexed_paths = {a["path"] for a in index.get("articles", [])}
    actual_paths = {str(wf.relative_to(KB_ROOT)) for wf in wiki_files}
    for missing in actual_paths - indexed_paths:
        issues.append(("WARN", f"wiki article not in index: {missing}"))
    for stale in indexed_paths - actual_paths:
        issues.append(("WARN", f"index references missing article: {stale}"))

    # 5. Check for orphaned source files (including _meta.json)
    manifest_sources = {item.get("source_path", "") for item in items.values()}
    manifest_metas = {item.get("meta_path", "") for item in items.values()}
    for sf in SOURCES_DIR.iterdir():
        if sf.name == ".gitkeep":
            continue
        rel = str(sf.relative_to(KB_ROOT))
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

    # index
    sub.add_parser("index", help="Rebuild _index.json from wiki/")

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
        "index": cmd_index,
        "search": cmd_search,
        "stats": cmd_stats,
        "health": cmd_health,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
