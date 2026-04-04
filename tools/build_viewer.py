"""KB Wiki Viewer Generator

Reads all wiki/*.md articles, parses YAML frontmatter,
and generates a single self-contained HTML viewer.

Usage:
    python tools/build_viewer.py          # generates wiki/viewer.html
    python tools/build_viewer.py --open   # generates and opens in browser
"""

import json
import re
import sys
from pathlib import Path

KB_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = KB_ROOT / "wiki"
SOURCES_DIR = KB_ROOT / "sources"
OUTPUT = WIKI_DIR / "viewer.html"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from markdown."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text

    raw, body = m.group(1), m.group(2)
    meta: dict = {}

    # Minimal YAML parser (no PyYAML dependency)
    current_key = None
    current_list: list[str] | None = None

    for line in raw.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        # List item
        if stripped.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
            current_list.append(stripped[2:].strip().strip('"').strip("'"))
            meta[current_key] = current_list
            continue

        # Multiline scalar continuation (summary: >)
        if current_key and current_key in meta and isinstance(meta[current_key], str):
            if not re.match(r"^\w[\w_-]*:", line):
                meta[current_key] = meta[current_key] + " " + stripped
                continue

        # Key: value
        kv = re.match(r"^([\w_-]+):\s*(.*)", line)
        if kv:
            current_key = kv.group(1)
            val = kv.group(2).strip().strip('"').strip("'")
            current_list = None
            if val == ">" or val == "|":
                meta[current_key] = ""
            elif val:
                meta[current_key] = val
            else:
                meta[current_key] = []
            continue

    return meta, body


def build_source_url_map() -> dict[str, str]:
    """Map source_id -> original URL by scanning sources/ directory."""
    url_map: dict[str, str] = {}
    for f in SOURCES_DIR.glob("*"):
        # Extract source_id from filename: {source_id}_{rest}
        parts = f.name.split("_", 1)
        if len(parts) < 2:
            continue
        source_id = parts[0]
        if source_id in url_map:
            continue

        try:
            content = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        # .clip JSON files have "url" field
        if f.suffix == ".clip":
            try:
                data = json.loads(content)
                url = data.get("url", "")
                if url and url.startswith(("http://", "https://")):
                    url_map[source_id] = url
                else:
                    # Fallback: extract URL from user_comment
                    comment = data.get("user_comment") or ""
                    m = re.search(r'https?://\S+', comment)
                    if m:
                        url_map[source_id] = m.group(0)
            except json.JSONDecodeError:
                pass
            continue

        # Source markdown files have "Source: https://..." line
        if f.suffix == ".md":
            for line in content.split("\n")[:10]:
                m = re.match(r"^Source:\s*(https?://\S+)", line.strip())
                if m:
                    url_map[source_id] = m.group(1)
                    break
            # Also check frontmatter for source_url
            meta, _ = parse_frontmatter(content)
            if url := meta.get("source_url"):
                url_map.setdefault(source_id, url)

    return url_map


def load_articles() -> list[dict]:
    # Try _index.json first (has deterministic source_urls + published_at)
    index_path = KB_ROOT / "_index.json"
    index_data: dict = {}
    if index_path.exists():
        try:
            index_data = json.loads(index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # Build article_id -> index entry lookup
    idx_lookup: dict[str, dict] = {}
    for a in index_data.get("articles", []):
        idx_lookup[a.get("id", "")] = a

    # Fallback URL map for articles not in index
    url_map = build_source_url_map() if not idx_lookup else {}

    articles = []
    for f in sorted(WIKI_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        aid = meta.get("article_id", f.stem)
        title = meta.get("title", f.stem.replace("-", " ").title())

        # Prefer index data for source_urls / published_at
        idx_entry = idx_lookup.get(aid, {})
        source_urls = idx_entry.get("source_urls", [])
        if not source_urls:
            source_ids = meta.get("source_ids", [])
            if isinstance(source_ids, str):
                source_ids = [source_ids]
            source_urls = [url_map[sid] for sid in source_ids if sid in url_map]

        published_at = idx_entry.get("published_at", meta.get("published_at", ""))

        articles.append({
            "id": aid,
            "title": title,
            "topics": meta.get("topics", []),
            "summary": meta.get("summary", "").strip(),
            "published_at": published_at,
            "created_at": meta.get("created_at", ""),
            "updated_at": meta.get("updated_at", ""),
            "source_urls": source_urls,
            "body": body.strip(),
            "filename": f.name,
        })
    # Sort by date descending
    articles.sort(key=lambda a: a.get("updated_at", ""), reverse=True)
    return articles



_WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

def _resolve_wiki_links(body: str, articles: list[dict]) -> str:
    """Replace [[ref]] wiki-links in body with markdown links."""
    # Build lookup: id -> title, title -> id
    by_id = {a['id']: a['title'] for a in articles}
    by_title = {a['title']: a['id'] for a in articles}

    def _replace(m):
        ref = m.group(1)
        # Exact match by id
        if ref in by_id:
            return f'[{by_id[ref]}](#{ref})'
        # Exact match by title
        if ref in by_title:
            aid = by_title[ref]
            return f'[{ref}](#{aid})'
        # Fuzzy: ref is substring of title or title is substring of ref
        for a in articles:
            if ref in a['title'] or a['title'] in ref:
                return f'[{a["title"]}](#{a["id"]})'
        # Fuzzy: significant shared prefix (>= 6 chars)
        ref_lower = ref.lower()
        for a in articles:
            t_lower = a['title'].lower()
            # Check common prefix length
            plen = 0
            for c1, c2 in zip(ref_lower, t_lower):
                if c1 == c2:
                    plen += 1
                else:
                    break
            if plen >= 6:
                return f'[{a["title"]}](#{a["id"]})'
        # No match - render as plain text
        return ref

    # Ensure wiki-links at line start become list items
    body = re.sub(r'^(?=\[\[)', '- ', body, flags=re.MULTILINE)
    return _WIKI_LINK_RE.sub(_replace, body)

def build_html(articles: list[dict]) -> str:
    # Collect all topics
    all_topics = sorted({t for a in articles for t in a["topics"]})
    # Resolve wiki-links in body before embedding
    for a in articles:
        a['body'] = _resolve_wiki_links(a['body'], articles)
    articles_json = json.dumps(articles, ensure_ascii=False)
    topics_json = json.dumps(all_topics, ensure_ascii=False)

    return f"""\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KB Wiki Viewer</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3/dist/purify.min.js"></script>
<style>
:root {{
  --bg: #0d1117;
  --surface: #161b22;
  --border: #30363d;
  --text: #e6edf3;
  --text-dim: #8b949e;
  --accent: #58a6ff;
  --accent-dim: #1f6feb33;
  --tag-bg: #1f6feb22;
  --tag-text: #58a6ff;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  height: 100vh;
  overflow: hidden;
  display: flex;
}}

/* --- Sidebar --- */
.sidebar {{
  width: 360px;
  min-width: 360px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  height: 100vh;
}}
.sidebar-header {{
  padding: 16px;
  border-bottom: 1px solid var(--border);
}}
.sidebar-header h1 {{
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  color: var(--text);
}}
.search-box {{
  width: 100%;
  padding: 8px 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 14px;
  outline: none;
}}
.search-box:focus {{
  border-color: var(--accent);
}}
.search-box::placeholder {{
  color: var(--text-dim);
}}

/* Topic filters */
.topic-filters {{
  padding: 8px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-height: 100px;
  overflow-y: auto;
}}
.topic-btn {{
  padding: 2px 8px;
  font-size: 11px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: transparent;
  color: var(--text-dim);
  cursor: pointer;
  white-space: nowrap;
}}
.topic-btn:hover {{
  border-color: var(--accent);
  color: var(--accent);
}}
.topic-btn.active {{
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent);
}}

/* Article list */
.article-list {{
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}}
.article-item {{
  padding: 10px 16px;
  cursor: pointer;
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}}
.article-item:hover {{
  background: var(--accent-dim);
}}
.article-item.active {{
  background: var(--accent-dim);
  border-left: 3px solid var(--accent);
  padding-left: 13px;
}}
.article-item-title {{
  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 4px;
}}
.article-item-meta {{
  font-size: 11px;
  color: var(--text-dim);
  display: flex;
  gap: 8px;
  align-items: center;
}}
.article-item-topics {{
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 4px;
}}
.article-item-topics .tag {{
  font-size: 10px;
  padding: 1px 6px;
  background: var(--tag-bg);
  color: var(--tag-text);
  border-radius: 8px;
}}
.count-badge {{
  padding: 2px 10px;
  font-size: 12px;
  color: var(--text-dim);
  text-align: center;
  border-top: 1px solid var(--border);
}}

/* --- Content area --- */
.content {{
  flex: 1;
  overflow-y: auto;
  padding: 40px 60px;
}}
.content.empty {{
  display: flex;
  align-items: center;
  justify-content: center;
}}
.empty-msg {{
  color: var(--text-dim);
  font-size: 14px;
}}

/* Markdown styling */
.content h1 {{ font-size: 28px; font-weight: 700; margin: 0 0 8px 0; line-height: 1.3; }}
.content .article-meta-header {{
  font-size: 13px;
  color: var(--text-dim);
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}}
.content .article-meta-header .tag {{
  font-size: 11px;
  padding: 2px 8px;
  background: var(--tag-bg);
  color: var(--tag-text);
  border-radius: 10px;
  margin-right: 4px;
}}
.content h2 {{ font-size: 20px; font-weight: 600; margin: 32px 0 12px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }}
.content h3 {{ font-size: 16px; font-weight: 600; margin: 24px 0 8px; }}
.content p {{ margin: 12px 0; line-height: 1.7; font-size: 15px; }}
.content ul, .content ol {{ margin: 8px 0 8px 24px; line-height: 1.7; }}
.content li {{ margin: 4px 0; font-size: 15px; }}
.content code {{
  background: var(--bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Cascadia Code', 'Fira Code', monospace;
}}
.content pre {{
  background: var(--bg);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
  border: 1px solid var(--border);
}}
.content pre code {{
  padding: 0;
  background: none;
}}
.content blockquote {{
  border-left: 3px solid var(--accent);
  padding: 4px 16px;
  margin: 12px 0;
  color: var(--text-dim);
}}
.content table {{
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
  font-size: 14px;
}}
.content th, .content td {{
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
}}
.content th {{
  background: var(--surface);
  font-weight: 600;
}}
.content a {{
  color: var(--accent);
  text-decoration: none;
}}
.content a:hover {{
  text-decoration: underline;
}}
.wiki-link {{
  color: var(--accent);
  cursor: pointer;
}}
.wiki-link:hover {{
  text-decoration: underline;
}}
.wiki-link.broken {{
  color: var(--text-dim);
  cursor: default;
  text-decoration: line-through;
}}
.content strong {{ color: #f0f6fc; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--text-dim); }}
</style>
</head>
<body>

<div class="sidebar">
  <div class="sidebar-header">
    <h1>KB Wiki</h1>
    <input type="text" class="search-box" id="search" placeholder="Search articles..." autofocus>
  </div>
  <div class="topic-filters" id="topicFilters"></div>
  <div class="article-list" id="articleList"></div>
  <div class="count-badge" id="countBadge"></div>
</div>

<div class="content empty" id="content">
  <div class="empty-msg">Select an article from the sidebar</div>
</div>

<script>
const ARTICLES = {articles_json};
const ALL_TOPICS = {topics_json};

let activeTopic = null;
let activeArticleId = null;

// Wiki-link lookup: map id and title to article
const wikiLookup = new Map();
ARTICLES.forEach(a => {{
  wikiLookup.set(a.id, a);
  wikiLookup.set(a.title, a);
}});

// Helper: create text node safely
function text(str) {{ return document.createTextNode(str); }}

// Helper: create element with attributes
function el(tag, attrs, children) {{
  const e = document.createElement(tag);
  if (attrs) Object.entries(attrs).forEach(([k, v]) => {{
    if (k === 'className') e.className = v;
    else if (k === 'onclick') e.addEventListener('click', v);
    else e.setAttribute(k, v);
  }});
  if (children) {{
    if (typeof children === 'string') e.appendChild(text(children));
    else if (Array.isArray(children)) children.forEach(c => {{ if (c) e.appendChild(c); }});
    else e.appendChild(children);
  }}
  return e;
}}

// --- Topic filters ---
const topicFilters = document.getElementById('topicFilters');
ALL_TOPICS.forEach(t => {{
  const btn = el('button', {{
    className: 'topic-btn',
    onclick: () => {{
      if (activeTopic === t) {{
        activeTopic = null;
        btn.classList.remove('active');
      }} else {{
        activeTopic = t;
        topicFilters.querySelectorAll('.topic-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }}
      renderList();
    }}
  }}, t);
  topicFilters.appendChild(btn);
}});

// --- Search ---
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', renderList);

function getFiltered() {{
  const q = searchInput.value.toLowerCase().trim();
  return ARTICLES.filter(a => {{
    if (activeTopic && !a.topics.includes(activeTopic)) return false;
    if (!q) return true;
    return a.title.toLowerCase().includes(q)
      || a.summary.toLowerCase().includes(q)
      || a.topics.some(t => t.includes(q))
      || a.body.toLowerCase().includes(q);
  }});
}}

// --- Article list ---
const articleListEl = document.getElementById('articleList');
const countBadge = document.getElementById('countBadge');

function renderList() {{
  articleListEl.replaceChildren();
  const filtered = getFiltered();
  filtered.forEach(a => {{
    const topicTags = a.topics.slice(0, 4).map(t => el('span', {{ className: 'tag' }}, t));
    const item = el('div', {{
      className: 'article-item' + (a.id === activeArticleId ? ' active' : ''),
      onclick: () => showArticle(a)
    }}, [
      el('div', {{ className: 'article-item-title' }}, a.title),
      el('div', {{ className: 'article-item-meta' }}, [
        el('span', {{}}, a.updated_at || a.created_at || '')
      ]),
      el('div', {{ className: 'article-item-topics' }}, topicTags)
    ]);
    articleListEl.appendChild(item);
  }});
  countBadge.textContent = filtered.length + ' / ' + ARTICLES.length + ' articles';
}}

// --- Show article ---
const contentEl = document.getElementById('content');

function showArticle(a) {{
  activeArticleId = a.id;
  renderList();
  contentEl.classList.remove('empty');
  contentEl.replaceChildren();

  // Title
  contentEl.appendChild(el('h1', {{}}, a.title));

  // Meta header
  const metaDiv = el('div', {{ className: 'article-meta-header' }});
  const dateLine = a.updated_at || a.created_at || '';
  const pubLine = a.published_at ? 'published: ' + a.published_at : '';
  const metaLine = [pubLine, dateLine, a.filename].filter(Boolean).join(' \\u00B7 ');
  metaDiv.appendChild(el('span', {{}}, metaLine));
  metaDiv.appendChild(document.createElement('br'));
  a.topics.forEach(t => {{
    metaDiv.appendChild(el('span', {{ className: 'tag' }}, t));
    metaDiv.appendChild(text(' '));
  }});
  if (a.source_urls && a.source_urls.length > 0) {{
    const srcDiv = el('div', {{ style: 'margin-top:8px' }});
    a.source_urls.forEach((url, i) => {{
      if (i > 0) srcDiv.appendChild(text(' '));
      const hostname = url.replace(/^https?:\\/\\//, '').split('/')[0];
      const link = el('a', {{ href: url, target: '_blank', rel: 'noopener', style: 'font-size:12px' }}, '\\u2197 ' + hostname);
      srcDiv.appendChild(link);
    }});
    metaDiv.appendChild(srcDiv);
  }}
  if (a.summary) {{
    const p = el('p', {{ style: 'margin-top:8px;color:var(--text-dim)' }}, a.summary);
    metaDiv.appendChild(p);
  }}
  contentEl.appendChild(metaDiv);

  // Body: render markdown, sanitize, handle internal links (DOMPurify applied)
  const rawHtml = marked.parse(a.body);
  const cleanHtml = DOMPurify.sanitize(rawHtml);
  const bodyDiv = document.createElement('div');
  bodyDiv.innerHTML = cleanHtml;  // safe: DOMPurify sanitized
  bodyDiv.addEventListener('click', (e) => {{
    const link = e.target.closest('a[href^="#"]');
    if (!link) return;
    e.preventDefault();
    const aid = link.getAttribute('href').slice(1);
    const target = wikiLookup.get(aid);
    if (target) showArticle(target);
  }});
  contentEl.appendChild(bodyDiv);

  contentEl.scrollTop = 0;
}}

// --- Keyboard nav ---
document.addEventListener('keydown', (e) => {{
  if (e.key === 'Escape') {{
    searchInput.value = '';
    activeTopic = null;
    topicFilters.querySelectorAll('.topic-btn').forEach(b => b.classList.remove('active'));
    renderList();
    searchInput.focus();
  }}
  if (e.key === '/' && document.activeElement !== searchInput) {{
    e.preventDefault();
    searchInput.focus();
  }}
}});

// Init
renderList();
</script>
</body>
</html>"""


def main():
    articles = load_articles()
    html = build_html(articles)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Generated {OUTPUT}  ({len(articles)} articles)")

    if "--open" in sys.argv:
        import webbrowser
        webbrowser.open(str(OUTPUT))


if __name__ == "__main__":
    main()
