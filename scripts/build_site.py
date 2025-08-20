#!/usr/bin/env python3
"""
Build a static HTML page at docs/index.html from library.bib, grouped by tags.

- Uses BibTeX `keywords` (comma or semicolon separated)
- Renders a Tag Index + per-tag sections
- Includes a client-side search box (filters by title, authors, venue, year, tag)
- No external assets; single self-contained file

Requires:
  pip install bibtexparser
"""

import re
import html
from pathlib import Path

import bibtexparser

ROOT = Path(__file__).resolve().parents[1]
BIB_PATH = ROOT / "library.bib"
DOCS_DIR = ROOT / "docs"
OUT = DOCS_DIR / "index.html"

def norm_keywords(value: str):
    if not value:
        return []
    raw = re.split(r"[;,]", value)
    cleaned = [w.strip() for w in raw if w.strip()]
    # (group_key, display_label)
    return [(w.lower(), w.strip()) for w in cleaned]

def format_authors(persons: str):
    if not persons:
        return ""
    parts = [p.strip() for p in re.split(r"\s+and\s+", persons)]
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} & {parts[1]}"
    return f"{parts[0]} et al."

def entry_sort_key(e):
    author = (e.get("author") or "").lower()
    year = e.get("year") or "9999"
    title = (e.get("title") or "").lower()
    return (author, year, title)

def entry_html(e):
    key = e.get("ID", "")
    typ = (e.get("ENTRYTYPE") or "").capitalize()
    title = (e.get("title") or "").strip(" {}")
    authors = format_authors(e.get("author") or "")
    year = e.get("year") or ""
    venue = e.get("journal") or e.get("booktitle") or e.get("publisher") or ""
    doi = (e.get("doi") or "").strip()
    url = (e.get("url") or "").strip()
    tags = [label.title() for _, label in norm_keywords(e.get("keywords","") or e.get("keyword",""))]

    safe = lambda s: html.escape(s, quote=True)

    bits = []
    if title:
        bits.append(f"<span class='title'><strong>{safe(title)}</strong></span>")
    meta_parts = []
    if authors: meta_parts.append(safe(authors))
    if year:    meta_parts.append(safe(str(year)))
    if venue:   meta_parts.append(safe(venue))
    if typ:     meta_parts.append(safe(typ))
    if meta_parts:
        bits.append(" — " + ", ".join(meta_parts))

    tail = []
    if doi:
        tail.append(f"<a href='https://doi.org/{safe(doi)}' target='_blank' rel='noopener'>DOI: {safe(doi)}</a>")
    if url:
        tail.append(f"<a href='{safe(url)}' target='_blank' rel='noopener'>Link</a>")

    tags_html = ""
    if tags:
        tags_html = " ".join(f"<span class='tag'>{safe(t)}</span>" for t in tags)

    dataset_text = " ".join([
        title or "",
        authors or "",
        venue or "",
        year or "",
        " ".join(tags)
    ]).lower()

    line = f"""
<li class="entry" data-text="{html.escape(dataset_text)}">
  <a id="{safe(key)}"></a>
  <div class="entry-main">{''.join(bits)}
    {' · ' + ' · '.join(tail) if tail else ''}
  </div>
  <div class="entry-tags">{tags_html}</div>
</li>""".strip()
    return line

def build():
    if not BIB_PATH.exists():
        raise SystemExit(f"Missing {BIB_PATH} — export your library to BibTeX as 'library.bib'.")

    with open(BIB_PATH, "r", encoding="utf-8") as f:
        db = bibtexparser.load(f)

    groups = {}
    untagged = []

    for e in db.entries:
        kws = norm_keywords(e.get("keywords","") or e.get("keyword",""))
        if not kws:
            untagged.append(e)
        else:
            for gkey, label in kws:
                display = label.capitalize()
                groups.setdefault(gkey, {"label": display, "entries": []})
                groups[gkey]["entries"].append(e)

    ordered_groups = sorted(groups.values(), key=lambda g: g["label"].lower())

    # Build Tag Index
    tag_index_html = ""
    if ordered_groups:
        links = " · ".join(
            f"<a href='#{g['label'].lower().replace(' ', '-')}'>{html.escape(g['label'])}</a>"
            for g in ordered_groups
        )
        tag_index_html = f"<nav class='tag-index'>{links}</nav>"

    # Build sections
    sections = []
    for g in ordered_groups:
        section_items = "\n".join(entry_html(e) for e in sorted(g["entries"], key=entry_sort_key))
        sections.append(f"""
<section id="{g['label'].lower().replace(' ', '-')}" class="tag-section">
  <h2>{html.escape(g['label'])}</h2>
  <ul class="entries">
    {section_items}
  </ul>
</section>""".strip())

    if untagged:
        section_items = "\n".join(entry_html(e) for e in sorted(untagged, key=entry_sort_key))
        sections.append(f"""
<section id="untagged" class="tag-section">
  <h2>(Untagged)</h2>
  <ul class="entries">
    {section_items}
  </ul>
</section>""".strip())

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Reference Library</title>
<style>
:root {{
  --fg: #111;
  --muted: #666;
  --bg: #fff;
  --chip: #eef;
  --chip-fg: #223;
  --border: #e5e7eb;
}}
html, body {{ margin: 0; padding: 0; background: var(--bg); color: var(--fg); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji"; }}
a {{ color: #0b63c0; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.container {{ max-width: 920px; margin: 0 auto; padding: 24px; }}
.header h1 {{ margin: 0 0 6px 0; }}
.header .meta {{ color: var(--muted); margin-bottom: 16px; }}
.search {{ position: sticky; top: 0; background: var(--bg); padding: 12px 0; border-bottom: 1px solid var(--border); z-index: 1; }}
.search input {{ width: 100%; padding: 10px 12px; font-size: 16px; border-radius: 8px; border: 1px solid var(--border); }}
.tag-index {{ margin: 12px 0 20px 0; line-height: 1.8; }}
.tag-index a {{ margin-right: 10px; white-space: nowrap; }}
.tag-section {{ margin: 28px 0; }}
.tag-section h2 {{ margin: 20px 0 8px 0; border-bottom: 1px solid var(--border); padding-bottom: 6px; }}
.entries {{ list-style: none; padding: 0; margin: 0; }}
.entry {{ padding: 10px 0; border-bottom: 1px dashed var(--border); }}
.entry .entry-main {{ }}
.entry .entry-tags {{ margin-top: 6px; }}
.tag {{ display: inline-block; background: var(--chip); color: var(--chip-fg); border-radius: 999px; padding: 2px 8px; margin-right: 6px; font-size: 12px; }}
.footer {{ color: var(--muted); font-size: 14px; margin-top: 40px; }}
.hidden {{ display: none !important; }}
</style>
</head>
<body>
<main class="container">
  <header class="header">
    <h1>Reference library</h1>
    <div class="meta">Generated from <code>library.bib</code>. Grouped by tag. Use the search below to filter.</div>
  </header>

  <div class="search">
    <input id="q" type="search" placeholder="Search title, authors, venue, year, or tag…" aria-label="Search references" />
  </div>

  {tag_index_html}

  {"".join(sections)}

  <div class="footer">
    <p>Built from <code>library.bib</code>. To update: replace the BibTeX and re-run <code>python scripts/build_site.py</code>.</p>
  </div>
</main>

<script>
(function() {{
  const q = document.getElementById('q');
  const sections = Array.from(document.querySelectorAll('.tag-section'));
  const entries = Array.from(document.querySelectorAll('.entry'));

  function applyFilter() {{
    const needle = (q.value || '').trim().toLowerCase();
    if (!needle) {{
      // show all
      entries.forEach(li => li.classList.remove('hidden'));
      sections.forEach(sec => sec.classList.remove('hidden'));
      // hide empty sections (none should be empty now)
      sections.forEach(sec => {{
        const anyVisible = Array.from(sec.querySelectorAll('.entry')).some(li => !li.classList.contains('hidden'));
        sec.classList.toggle('hidden', !anyVisible);
      }});
      return;
    }}
    entries.forEach(li => {{
      const hay = li.getAttribute('data-text') || '';
      li.classList.toggle('hidden', !hay.includes(needle));
    }});
    sections.forEach(sec => {{
      const anyVisible = Array.from(sec.querySelectorAll('.entry')).some(li => !li.classList.contains('hidden'));
      sec.classList.toggle('hidden', !anyVisible);
    }});
  }}

  q.addEventListener('input', applyFilter);
}})();
</script>

</body>
</html>
"""
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"Wrote site to {OUT}")

if __name__ == "__main__":
    build()