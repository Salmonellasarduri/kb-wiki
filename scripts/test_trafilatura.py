#!/usr/bin/env python3
"""Phase 0: Validate trafilatura extraction quality on sample URLs.

Reports success rate, format quality, title match, and average text length.
Run this before building the full Telegram Clip pipeline.

Usage:
    python scripts/test_trafilatura.py
    python scripts/test_trafilatura.py --urls https://example.com https://another.com
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import sys
import time
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Sample URLs (edit this list to match sites you actually read)
# ---------------------------------------------------------------------------
SAMPLE_URLS = [
    "https://simonwillison.net/2024/Nov/8/things-not-to-do/",
    "https://karpathy.github.io/2015/05/21/rnn-effectiveness/",
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://martinfowler.com/articles/bottlenecks-of-scaleups/01-tech-debt.html",
    "https://www.joelonsoftware.com/2000/08/09/the-joel-test-12-steps-to-better-code/",
    "https://paulgraham.com/greatwork.html",
    "https://en.wikipedia.org/wiki/Knowledge_management",
    "https://arxiv.org/abs/2305.10601",
    "https://zenn.dev/qnighy/articles/d4f8bb4e4e2f57",
    "https://note.com/shi3zblog/n/n1b14e39f4581",
]


def safe_fetch(url: str, timeout: int = 15, max_bytes: int = 5_000_000) -> str | None:
    """Fetch URL with basic safety checks. Returns HTML or None."""
    import requests

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        print(f"  SKIP: unsupported scheme {parsed.scheme}")
        return None

    hostname = parsed.hostname
    if not hostname:
        print(f"  SKIP: no hostname")
        return None

    # Basic private IP check
    try:
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
            print(f"  SKIP: private IP {ip}")
            return None
    except socket.gaierror:
        print(f"  SKIP: DNS resolution failed")
        return None

    try:
        resp = requests.get(
            url,
            timeout=(5, timeout),
            headers={"User-Agent": "Mozilla/5.0 (compatible; KBClipper/1.0)"},
            stream=True,
        )
        resp.raise_for_status()

        chunks = []
        total = 0
        for chunk in resp.iter_content(chunk_size=8192):
            total += len(chunk)
            if total > max_bytes:
                print(f"  SKIP: response too large (>{max_bytes} bytes)")
                return None
            chunks.append(chunk)

        return b"".join(chunks).decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  FETCH ERROR: {e}")
        return None


def test_extraction(url: str) -> dict:
    """Test trafilatura extraction on a single URL."""
    import trafilatura

    result = {
        "url": url,
        "fetch_ok": False,
        "extract_ok": False,
        "title": None,
        "text_length": 0,
        "text_preview": "",
        "error": None,
    }

    html = safe_fetch(url)
    if html is None:
        result["error"] = "fetch_failed"
        return result

    result["fetch_ok"] = True

    # Extract with trafilatura
    text = trafilatura.extract(html, output_format="txt", include_comments=False)
    meta = trafilatura.bare_extraction(html)

    if text and len(text.strip()) > 50:
        result["extract_ok"] = True
        result["text_length"] = len(text)
        result["text_preview"] = text[:200].replace("\n", " ")

    if meta:
        result["title"] = getattr(meta, "title", None)

    if not result["extract_ok"]:
        result["error"] = "extraction_empty_or_short"

    return result


def main():
    parser = argparse.ArgumentParser(description="Test trafilatura extraction quality")
    parser.add_argument("--urls", nargs="*", help="URLs to test (default: built-in sample list)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    urls = args.urls or SAMPLE_URLS

    # Check dependencies
    try:
        import trafilatura  # noqa: F401
    except ImportError:
        print("ERROR: trafilatura not installed. Run: pip install trafilatura")
        return 2
    try:
        import requests  # noqa: F401
    except ImportError:
        print("ERROR: requests not installed. Run: pip install requests")
        return 2

    print(f"Testing {len(urls)} URLs...\n")

    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        r = test_extraction(url)
        results.append(r)

        status = "OK" if r["extract_ok"] else ("FETCH_FAIL" if not r["fetch_ok"] else "EXTRACT_FAIL")
        print(f"  {status}", end="")
        if r["title"]:
            print(f" | title: {r['title'][:60]}", end="")
        if r["text_length"]:
            print(f" | {r['text_length']} chars", end="")
        print()

        time.sleep(1)  # polite delay

    # Summary
    total = len(results)
    fetch_ok = sum(1 for r in results if r["fetch_ok"])
    extract_ok = sum(1 for r in results if r["extract_ok"])
    avg_len = (
        sum(r["text_length"] for r in results if r["extract_ok"]) // max(extract_ok, 1)
    )

    print(f"\n{'='*50}")
    print(f"RESULTS: {total} URLs tested")
    print(f"  Fetch success:   {fetch_ok}/{total} ({100*fetch_ok//total}%)")
    print(f"  Extract success: {extract_ok}/{total} ({100*extract_ok//total}%)")
    print(f"  Avg text length: {avg_len} chars (extracted only)")
    print(f"  With title:      {sum(1 for r in results if r['title'])}/{total}")

    if extract_ok / max(total, 1) >= 0.7:
        print(f"\n  >>> GO: {100*extract_ok//total}% success rate meets 70% threshold")
    elif extract_ok / max(total, 1) >= 0.5:
        print(f"\n  >>> CAUTION: {100*extract_ok//total}% success rate. Proceed with strong fallback.")
    else:
        print(f"\n  >>> NO-GO: {100*extract_ok//total}% success rate below 50%. Reconsider approach.")

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))

    # Show failures
    failures = [r for r in results if not r["extract_ok"]]
    if failures:
        print(f"\nFailed URLs ({len(failures)}):")
        for r in failures:
            print(f"  {r['url']} -- {r['error']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
