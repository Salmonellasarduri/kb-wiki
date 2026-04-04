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
import ipaddress
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

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
# Optional frontmatter fields (not validated as required)
FRONTMATTER_OPTIONAL = {
    "aliases_ja": list,  # Japanese aliases for search
}

COMPILE_MODEL = "claude-sonnet-4-20250514"
WATCH_DEBOUNCE_SEC = 3.0
MAX_SOURCE_BYTES = 200_000  # ~200KB, well within Claude's context window

# URL fetch limits
FETCH_WIRE_MAX = 5_000_000       # 5MB wire size
FETCH_DECODED_MAX = 10_000_000   # 10MB decompressed
FETCH_TIMEOUT = (5, 15)          # (connect, read) seconds
FETCH_MAX_REDIRECTS = 5
FETCH_ALLOWED_PORTS = {80, 443}
FETCH_UA = "Mozilla/5.0 (compatible; KBClipper/1.0)"

# Telegram bot state
BOT_STATE_PATH = KB_ROOT / "kb_bot_state.json"

# URL normalization: tracking params to strip
URL_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "fbclid", "gclid", "gclsrc", "dclid", "msclkid",
    "mc_cid", "mc_eid", "ref", "ref_src", "ref_url",
}

# .clip JSON schema required fields
CLIP_REQUIRED_FIELDS = {"version", "url"}


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


def content_hash(text: str) -> str:
    """Compute SHA-256 hex digest of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# URL utilities
# ---------------------------------------------------------------------------

def normalize_url(url: str) -> str:
    """Normalize URL for dedup: lowercase scheme/host, strip tracking params + fragment."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path
    # Strip tracking params
    qs = parse_qs(parsed.query, keep_blank_values=False)
    cleaned = {k: v for k, v in qs.items() if k.lower() not in URL_TRACKING_PARAMS}
    query = urlencode(cleaned, doseq=True) if cleaned else ""
    return urlunparse((scheme, netloc, path, parsed.params, query, ""))


def _resolve_and_check_all_ips(hostname: str) -> None:
    """Resolve hostname and check ALL addresses are safe. Raises on blocked IP."""
    info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    if not info:
        raise ValueError(f"DNS resolution failed for {hostname}")
    for entry in info:
        ip_str = entry[4][0]
        ip = ipaddress.ip_address(ip_str)
        if _is_ip_blocked(ip):
            raise ValueError(f"Blocked IP: {ip} ({hostname})")


def _is_ip_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Check if IP is private, loopback, link-local, or reserved."""
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
    )


def _validate_url_for_fetch(url: str) -> str:
    """Validate URL for safe fetching. Returns validated URL or raises ValueError."""
    parsed = urlparse(url)

    # Scheme check
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported scheme: {parsed.scheme}")

    # Hostname check
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("No hostname in URL")

    # Reject userinfo (user:pass@host)
    if parsed.username or parsed.password:
        raise ValueError("URL with userinfo not allowed")

    # Port check
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if port not in FETCH_ALLOWED_PORTS:
        raise ValueError(f"Port {port} not allowed (only 80/443)")

    # DNS resolve + check ALL IPs
    _resolve_and_check_all_ips(hostname)

    return url


def safe_fetch(url: str) -> tuple[str, str, str | None]:
    """Fetch URL with SSRF hardening and size limits.

    Manually follows redirects to re-validate IP at each hop.

    Returns:
        (html_text, final_url, page_title_or_none)

    Raises:
        RuntimeError on fetch failure.
    """
    import requests

    session = requests.Session()
    session.trust_env = False  # ignore proxy env vars
    session.max_redirects = 0  # we handle redirects manually

    current_url = url
    for hop in range(FETCH_MAX_REDIRECTS + 1):
        # Validate each hop
        try:
            _validate_url_for_fetch(current_url)
        except ValueError as e:
            raise RuntimeError(f"URL validation failed (hop {hop}): {e}")

        try:
            resp = session.get(
                current_url,
                timeout=FETCH_TIMEOUT,
                allow_redirects=False,
                headers={"User-Agent": FETCH_UA},
                stream=True,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}")

        # Handle redirect
        if resp.is_redirect and "location" in resp.headers:
            current_url = resp.headers["location"]
            # Resolve relative redirects
            if not urlparse(current_url).scheme:
                from urllib.parse import urljoin
                current_url = urljoin(resp.url, current_url)
            resp.close()
            continue

        # Non-redirect response
        if resp.status_code >= 400:
            resp.close()
            raise RuntimeError(f"HTTP {resp.status_code}")

        # Content-Type check (allow html-like)
        ct = (resp.headers.get("Content-Type") or "").lower()
        if not any(t in ct for t in ("text/html", "application/xhtml+xml")):
            # Sniff: read first 1KB and check for HTML tags
            peek = resp.raw.read(1024)
            if b"<html" not in peek.lower() and b"<!doctype" not in peek.lower():
                resp.close()
                raise RuntimeError(f"Not HTML: Content-Type={ct}")
            # Put peek back by reading the rest
            chunks = [peek]
            total = len(peek)
        else:
            chunks = []
            total = 0

        # Read body with size limit
        for chunk in resp.iter_content(chunk_size=8192):
            total += len(chunk)
            if total > FETCH_WIRE_MAX:
                resp.close()
                raise RuntimeError(f"Response too large (>{FETCH_WIRE_MAX} bytes)")
            chunks.append(chunk)

        resp.close()
        raw_bytes = b"".join(chunks)

        # Decompressed size check (requests handles decompression transparently)
        if len(raw_bytes) > FETCH_DECODED_MAX:
            raise RuntimeError(f"Decoded content too large (>{FETCH_DECODED_MAX} bytes)")

        html = raw_bytes.decode("utf-8", errors="replace")

        # Extract title from HTML
        title = None
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if title_match:
            import html as html_mod
            title = html_mod.unescape(title_match.group(1)).strip()[:200]

        return html, current_url, title

    raise RuntimeError(f"Too many redirects (>{FETCH_MAX_REDIRECTS})")


def extract_article_text(html: str) -> str | None:
    """Extract main article text from HTML using trafilatura."""
    try:
        import trafilatura
    except ImportError:
        print("ERROR: trafilatura not installed. Run: pip install trafilatura")
        return None

    text = trafilatura.extract(html, output_format="txt", include_comments=False)
    if text and len(text.strip()) > 50:
        return text.strip()
    return None


def parse_clip_file(path: Path) -> dict | None:
    """Parse and validate a .clip JSON file. Returns dict or None on error."""
    try:
        raw = path.read_text(encoding="utf-8")
        if len(raw) > 100_000:  # 100KB sanity limit for .clip JSON
            print(f"ERROR: .clip too large: {path.name} ({len(raw)} bytes)")
            return None
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"ERROR: cannot parse .clip {path.name}: {e}")
        return None

    if not isinstance(data, dict):
        print(f"ERROR: .clip {path.name}: not a JSON object")
        return None

    # Schema validation
    missing = CLIP_REQUIRED_FIELDS - set(data.keys())
    if missing:
        print(f"ERROR: .clip {path.name}: missing fields: {missing}")
        return None

    url = data.get("url", "")
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        print(f"ERROR: .clip {path.name}: invalid url")
        return None

    return data


def build_source_markdown(
    url: str,
    title: str | None,
    article_text: str | None,
    user_comment: str | None,
    shared_title: str | None,
    fetch_status: str,
) -> str:
    """Build a markdown source file from clip data."""
    parts = []

    # Use fetched title, fallback to shared title
    display_title = title or shared_title or url
    parts.append(f"# {display_title}\n")
    parts.append(f"Source: {url}\n")

    if user_comment:
        parts.append(f"\n> {user_comment}\n")

    if article_text:
        parts.append(f"\n{article_text}\n")
    else:
        parts.append(f"\nFetch status: {fetch_status}\n")
        if title:
            parts.append(f"Title: {title}\n")

    return "\n".join(parts)


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

def _generate_source_id(fhash: str, items: dict) -> str | None:
    """Generate source_id from hash, extending on collision. Returns None on failure."""
    source_id = fhash[:HASH_DISPLAY_LEN]
    while source_id in items and items[source_id]["hash"] != fhash:
        if len(source_id) >= len(fhash):
            return None
        source_id = fhash[:len(source_id) + 1]
    return source_id


def _ingest_clip_file(
    fpath: Path, manifest: dict, now: str,
) -> tuple[bool, str]:
    """Ingest a .clip file: parse, fetch URL, save source. Returns (success, message)."""
    items = manifest["items"]
    hash_index = manifest["_hash_index"]

    clip = parse_clip_file(fpath)
    if clip is None:
        return False, "invalid .clip"

    url = clip["url"]
    normalized = normalize_url(url)
    user_comment = clip.get("user_comment") or ""
    shared_title = clip.get("shared_title")

    # Dedupe by normalized URL (check existing sources for same URL)
    url_key = "clip:" + content_hash(normalized)
    if url_key in hash_index:
        existing_id = hash_index[url_key]
        return True, f"SKIP (duplicate URL): {normalized[:60]} -> {existing_id}"

    # Fetch and extract
    fetch_status = "pending"
    fetched_title = None
    article_text = None
    fetch_error = None
    final_url = None

    try:
        html, final_url, fetched_title = safe_fetch(url)
        article_text = extract_article_text(html)
        fetch_status = "ok" if article_text else "extraction_failed"
        if not article_text:
            fetch_error = "trafilatura returned empty or short text"
    except RuntimeError as e:
        fetch_status = "fetch_failed"
        fetch_error = str(e)[:200]
        print(f"  FETCH FAILED: {e}")

    # Build markdown source
    md = build_source_markdown(
        url=url,
        title=fetched_title,
        article_text=article_text,
        user_comment=user_comment if user_comment else None,
        shared_title=shared_title,
        fetch_status=fetch_status,
    )

    # Hash the produced markdown for content dedup
    fhash = content_hash(md)
    if fhash in hash_index:
        existing_id = hash_index[fhash]
        return True, f"SKIP (duplicate content): {fpath.name} -> {existing_id}"

    source_id = _generate_source_id(fhash, items)
    if source_id is None:
        return False, "hash collision"

    # Build slug from title (max 40 chars)
    slug_base = (fetched_title or shared_title or "clip")[:40]
    slug = sanitize_filename(slug_base).strip("_") or "clip"
    dest_name = f"{source_id}_{slug}.md"
    dest_path = SOURCES_DIR / dest_name
    meta_path = SOURCES_DIR / f"{source_id}_meta.json"

    # Write source markdown (atomic)
    try:
        import tempfile as _tf
        fd, tmp = _tf.mkstemp(dir=str(SOURCES_DIR), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(md)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, dest_path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    except OSError as e:
        return False, f"write failed: {e}"

    # Write meta with clip-specific fields
    meta = {
        "source_id": source_id,
        "hash": fhash,
        "original_name": fpath.name,
        "ingested_at": now,
        "clip_source": True,
        "fetch_url": url,
        "fetch_final_url": final_url if fetch_status == "ok" else None,
        "fetch_status": fetch_status,
        "fetch_error": fetch_error,
        "fetched_title": fetched_title,
        "shared_title": shared_title,
        "user_comment": user_comment[:500] if user_comment else None,
        "normalized_url": normalized,
    }
    atomic_write_json(meta_path, meta)

    # Update manifest
    hash_index[fhash] = source_id
    hash_index[url_key] = source_id  # URL-based dedup key
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

    status_label = "CLIPPED" if article_text else "CLIPPED (url-only)"
    return True, f"{status_label}: {url[:60]} -> {source_id}"


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
        # --- .clip files: URL fetch pipeline ---
        if fpath.suffix == ".clip":
            ok, msg = _ingest_clip_file(fpath, manifest, now)
            print(f"  {msg}")
            if ok:
                to_delete.append(fpath)
                if not msg.startswith("SKIP"):
                    ingested += 1
                else:
                    skipped_dup += 1
            else:
                errors += 1
            continue

        # --- Regular files: existing pipeline ---
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

        source_id = _generate_source_id(fhash, items)
        if source_id is None:
            print(f"ERROR: hash collision or corrupt manifest for {fpath.name}")
            errors += 1
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
aliases_ja:
  - Japanese reading or alias for each topic/entity (e.g. デブライネ, 量子コンピュータ)
summary: >
  2-3 sentence summary of the key concepts and conclusions.
  Be specific about entities, terminology, and actionable insights.
created_at: "{today}"
updated_at: "{today}"
---

Rules:
- article_id must be unique, descriptive, kebab-case
- topics must be kebab-case, lowercase
- aliases_ja: list Japanese readings/aliases for key topics, people, and entities mentioned in the article. Include katakana for foreign names, common Japanese terms for technical concepts. If the article is in Japanese, include the original Japanese terms. If no Japanese aliases apply, use an empty list []
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
            "aliases_ja": fm.get("aliases_ja", []),
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


def _telegram_polling_thread(
    token: str, chat_id: int, inbox_dir: Path, stop_event: threading.Event,
) -> None:
    """Telegram polling loop for use in a background thread."""
    import requests as _req

    state = _load_bot_state()
    offset = state.get("last_update_id", 0)
    processed_ids = set(state.get("processed_ids", []))

    while not stop_event.is_set():
        try:
            data = _telegram_api(token, "getUpdates", {
                "offset": offset + 1,
                "timeout": 10,  # shorter timeout for responsive shutdown
                "allowed_updates": '["message"]',
            })
        except _req.Timeout:
            continue
        except Exception as e:
            print(f"[telegram] Poll error: {e}")
            if stop_event.wait(5):
                break
            continue

        for update in data.get("result", []):
            if stop_event.is_set():
                break
            update_id = update["update_id"]
            offset = max(offset, update_id)

            msg = update.get("message")
            if not msg:
                continue

            msg_chat_id = msg.get("chat", {}).get("id")
            msg_id = msg.get("message_id", 0)
            dedup_key = f"{msg_chat_id}:{msg_id}"

            if msg_chat_id != chat_id or dedup_key in processed_ids:
                continue

            url = _extract_url_from_message(msg)
            if not url:
                processed_ids.add(dedup_key)
                continue

            comment = _extract_comment_from_message(msg, url)
            msg_date = msg.get("date", 0)
            clipped_at = (
                datetime.datetime.fromtimestamp(msg_date, tz=datetime.timezone.utc).isoformat()
                if msg_date else datetime.datetime.now(datetime.timezone.utc).isoformat()
            )

            clip_data = {
                "version": 1,
                "url": url,
                "shared_title": None,
                "user_comment": comment or None,
                "capture_channel": "telegram",
                "telegram_message_id": msg_id,
                "telegram_chat_id": msg_chat_id,
                "clipped_at": clipped_at,
            }

            clip_filename = f"clip_{msg_chat_id}_{msg_id}.clip"
            clip_path = inbox_dir / clip_filename
            try:
                atomic_write_json(clip_path, clip_data)
                print(f"  [telegram] CLIP: {url[:60]} -> {clip_filename}")
            except Exception as e:
                print(f"  [telegram] ERROR: {e}")
                continue

            processed_ids.add(dedup_key)

            # Reply
            try:
                _telegram_api(token, "sendMessage", {
                    "chat_id": chat_id,
                    "reply_to_message_id": msg_id,
                    "text": f"Clipped: {url[:50]}",
                })
            except Exception:
                pass

        # Save state (error-tolerant)
        try:
            state["last_update_id"] = offset
            state["processed_ids"] = list(processed_ids)
            _save_bot_state(state)
        except Exception as e:
            print(f"[telegram] WARNING: state save failed: {e}")

    print("[telegram] Polling stopped.")


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

    # Optional Telegram polling
    telegram_thread = None
    stop_event = threading.Event()
    use_telegram = getattr(args, "telegram", False)

    if use_telegram:
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id_str = os.environ.get("TELEGRAM_CHAT_ID", "")
        if token and chat_id_str:
            try:
                import requests  # noqa: F401
                me = _telegram_api(token, "getMe")
                bot_name = me["result"].get("username", "unknown")
                print(f"Telegram bot connected: @{bot_name}")
                telegram_thread = threading.Thread(
                    target=_telegram_polling_thread,
                    args=(token, int(chat_id_str), INBOX_DIR, stop_event),
                    name="telegram-poller",
                )
                telegram_thread.start()
            except Exception as e:
                print(f"WARNING: Telegram bot failed to start: {e}")
                print("Continuing with file watch only.")
        else:
            print("WARNING: --telegram requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars")

    print(f"Watching {INBOX_DIR} for new files... (Ctrl+C to stop)")
    print(f"Debounce: {WATCH_DEBOUNCE_SEC}s after last file event")

    sync_lock = threading.Lock()

    try:
        while True:
            time.sleep(0.5)
            if handler.pending and (time.time() - handler.last_event) >= WATCH_DEBOUNCE_SEC:
                handler.pending = False
                if sync_lock.acquire(blocking=False):
                    try:
                        print(f"\n{'='*50}")
                        print(f"New files detected. Running sync...")
                        print(f"{'='*50}\n")
                        cmd_sync(args)
                        print(f"\nWatching {INBOX_DIR}... (Ctrl+C to stop)")
                    finally:
                        sync_lock.release()
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        stop_event.set()
        observer.stop()

    observer.join()
    if telegram_thread:
        telegram_thread.join(timeout=15)
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
# Telegram Bot
# ---------------------------------------------------------------------------

URL_RE = re.compile(r"https?://[^\s<>\"']+")


def _extract_url_from_message(msg: dict) -> str | None:
    """Extract URL from Telegram message, preferring entities over regex."""
    text = msg.get("text") or msg.get("caption") or ""
    entities = msg.get("entities") or msg.get("caption_entities") or []

    # Prefer entity-based extraction
    for ent in entities:
        if ent.get("type") == "url":
            offset = ent["offset"]
            length = ent["length"]
            return text[offset:offset + length]
        if ent.get("type") == "text_link":
            return ent.get("url")

    # Fallback: regex
    m = URL_RE.search(text)
    return m.group(0) if m else None


def _extract_comment_from_message(msg: dict, url: str) -> str:
    """Extract user comment (text minus the URL)."""
    text = msg.get("text") or ""
    # Remove the URL from text to get the comment
    comment = text.replace(url, "").strip()
    # Clean up extra whitespace
    comment = re.sub(r"\s+", " ", comment).strip()
    return comment[:500]


def _telegram_api(token: str, method: str, params: dict | None = None) -> dict:
    """Call Telegram Bot API. Returns JSON response."""
    import requests
    url = f"https://api.telegram.org/bot{token}/{method}"
    resp = requests.get(url, params=params or {}, timeout=35)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data.get('description', 'unknown')}")
    return data


def _load_bot_state() -> dict:
    """Load bot state (last_update_id, processed_ids)."""
    return load_json(BOT_STATE_PATH) or {"last_update_id": 0, "processed_ids": []}


def _save_bot_state(state: dict) -> None:
    """Save bot state atomically."""
    # Keep processed_ids bounded
    ids = state.get("processed_ids", [])
    if len(ids) > 1000:
        state["processed_ids"] = ids[-500:]
    atomic_write_json(BOT_STATE_PATH, state)


def cmd_bot(args: argparse.Namespace) -> int:
    """Run Telegram bot: poll for messages, create .clip files in inbox/."""
    import requests as _requests  # noqa: F811 — verify import

    token = args.token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id_str = args.chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token:
        print("ERROR: --token or TELEGRAM_BOT_TOKEN required")
        return 2
    if not chat_id_str:
        print("ERROR: --chat-id or TELEGRAM_CHAT_ID required")
        return 2

    allowed_chat_id = int(chat_id_str)

    # Verify bot connection
    try:
        me = _telegram_api(token, "getMe")
        bot_name = me["result"].get("username", "unknown")
        print(f"Bot connected: @{bot_name}")
    except Exception as e:
        print(f"ERROR: Cannot connect to Telegram: {e}")
        return 2

    state = _load_bot_state()
    offset = state.get("last_update_id", 0)
    processed_ids = set(state.get("processed_ids", []))

    print(f"Polling for messages (chat_id={allowed_chat_id})... Ctrl+C to stop")

    try:
        while True:
            try:
                data = _telegram_api(token, "getUpdates", {
                    "offset": offset + 1,
                    "timeout": 30,
                    "allowed_updates": '["message"]',
                })
            except _requests.Timeout:
                continue
            except Exception as e:
                print(f"Poll error: {e}")
                time.sleep(5)
                continue

            for update in data.get("result", []):
                update_id = update["update_id"]
                offset = max(offset, update_id)

                msg = update.get("message")
                if not msg:
                    continue

                msg_chat_id = msg.get("chat", {}).get("id")
                msg_id = msg.get("message_id", 0)
                dedup_key = f"{msg_chat_id}:{msg_id}"

                # Chat allowlist
                if msg_chat_id != allowed_chat_id:
                    continue

                # Idempotency check
                if dedup_key in processed_ids:
                    continue

                # Extract URL
                url = _extract_url_from_message(msg)
                if not url:
                    # Reply: no URL found
                    try:
                        _telegram_api(token, "sendMessage", {
                            "chat_id": allowed_chat_id,
                            "reply_to_message_id": msg_id,
                            "text": "No URL found in message. Send a URL to clip.",
                        })
                    except Exception:
                        pass
                    processed_ids.add(dedup_key)
                    continue

                comment = _extract_comment_from_message(msg, url)
                msg_date = msg.get("date", 0)
                clipped_at = (
                    datetime.datetime.fromtimestamp(msg_date, tz=datetime.timezone.utc).isoformat()
                    if msg_date else datetime.datetime.now(datetime.timezone.utc).isoformat()
                )

                # Build .clip JSON
                clip_data = {
                    "version": 1,
                    "url": url,
                    "shared_title": None,
                    "user_comment": comment or None,
                    "capture_channel": "telegram",
                    "telegram_message_id": msg_id,
                    "telegram_chat_id": msg_chat_id,
                    "clipped_at": clipped_at,
                }

                # Write .clip to inbox/ (atomic)
                clip_filename = f"clip_{msg_chat_id}_{msg_id}.clip"
                clip_path = INBOX_DIR / clip_filename
                try:
                    atomic_write_json(clip_path, clip_data)
                    print(f"CLIP: {url[:60]} -> {clip_filename}")
                except Exception as e:
                    print(f"ERROR writing .clip: {e}")
                    continue

                # Mark processed AFTER successful .clip write
                processed_ids.add(dedup_key)

                # Reply: acknowledged
                try:
                    reply_text = f"Clipped: {url[:50]}"
                    if comment:
                        reply_text += f"\nNote: {comment[:100]}"
                    _telegram_api(token, "sendMessage", {
                        "chat_id": allowed_chat_id,
                        "reply_to_message_id": msg_id,
                        "text": reply_text,
                    })
                except Exception:
                    pass  # reply failure is non-critical

            # Save state after processing batch (error-tolerant)
            try:
                state["last_update_id"] = offset
                state["processed_ids"] = list(processed_ids)
                _save_bot_state(state)
            except Exception as e:
                print(f"WARNING: state save failed: {e}")

    except KeyboardInterrupt:
        print("\nStopping bot...")
        state["last_update_id"] = offset
        state["processed_ids"] = list(processed_ids)
        _save_bot_state(state)
        print("State saved.")

    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    # Load .env if present (for TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, etc.)
    env_path = KB_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

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
    p_watch = sub.add_parser("watch", help="Monitor inbox/ and auto-sync on new files")
    p_watch.add_argument(
        "--telegram", action="store_true",
        help="Also poll Telegram bot (requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars)",
    )

    # bot
    p_bot = sub.add_parser("bot", help="Run Telegram bot: poll messages and create .clip files")
    p_bot.add_argument("--token", help="Telegram Bot API token (or TELEGRAM_BOT_TOKEN env)")
    p_bot.add_argument("--chat-id", help="Allowed chat ID (or TELEGRAM_CHAT_ID env)")

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
        "bot": cmd_bot,
        "search": cmd_search,
        "stats": cmd_stats,
        "health": cmd_health,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
