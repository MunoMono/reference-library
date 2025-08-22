#!/usr/bin/env python3
"""
Build a static HTML page at docs/index.html from library.bib, grouped by:
- Zotero collections (if exported via Better BibTeX "Include collections")
- Tags (BibTeX keywords; comma/semicolon separated)

Adds minimal TeX cleanup for labels (e.g., {\textbar} -> |).
Outputs HTML that links to docs/styles.css (no inline CSS).

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
STYLES = DOCS_DIR / "styles.css"  # referenced by the HTML (must exist)

# ----------------------- helpers -----------------------
def clean_tex(s: str) -> str:
    if not s:
        return ""
    s = s.replace(r"{\textbar}", "|").replace(r"\textbar", "|")
    s = s.replace(r"\&", "&")
    s = re.sub(r"[{}]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def norm_keywords(value: str):
    if not value:
        return []
    raw = re.split(r"[;,]", value)
    cleaned = [clean_tex(w.strip()) for w in raw if w.strip()]
    return [(w.lower(), w) for w in cleaned]

def norm_list(value: str):
    if not value:
        return []
    raw = re.split(r"[;,\n]", value)
    return [clean_tex(w.strip()) for w in raw if w.strip()]

def entry_collections(e):
    return norm_list(e.get("collections") or e.get("groups") or "")

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
    tags = [label for _, label in norm_keywords(e.get("keywords","") or e.get("keyword",""))]
    colls = entry_collections(e)

    esc = lambda s: html.escape(s, quote=True)

    bits = []
    if title:
        bits.append(f"<span class='title'><strong>{esc(title)}</strong></span>")
    meta = []
    if authors: meta.append(esc(authors))
    if year:    meta.append(esc(str(year)))
    if venue:   meta.append(esc(venue))
    if typ:     meta.append(esc(typ))
    if meta:
        bits.append(" — " + ", ".join(meta))

    tail = []
    if doi:
        tail.append(f"<a href='https://doi.org/{esc(doi)}' target='_blank' rel='noopener'>DOI: {esc(doi)}</a>")
    if url:
        tail.append(f"<a href='{esc(url)}' target='_blank' rel='noopener'>Link</a>")

    tags_html = " ".join(f"<span class='tag'>{esc(t)}</span>" for t in tags) if tags else ""
    colls_html = " ".join(f"<span class='tag coll'>{esc(c)}</span>" for c in colls) if colls else ""

    dataset_text = " ".join([
        title or "", authors or "", venue or "", year or "",
        " ".join(tags), " ".join(colls)
    ]).lower()

    return f"""
<li class="entry" data-text="{html.escape(dataset_text)}">
  <a id="{esc(key)}"></a>
  <div class="entry-main">{''.join(bits)}
    {' · ' + ' · '.join(tail) if tail else ''}
  </div>
  <div class="entry-tags">{tags_html} {colls_html}</div>
</li>""".strip()
# -------------------------------------------------------


def build():
    if not BIB_PATH.exists():
        raise SystemExit(f"Missing {BIB_PATH} — export your library to BibTeX as 'library.bib'.")

    with open(BIB_PATH, "r", encoding="utf-8") as f:
        db = bibtexparser.load(f)

    # Collections groups
    coll_groups = {}
    for e in db.entries:
        for path in entry_collections(e):
            k = path.lower()
            coll_groups.setdefault(k, {"label": path, "entries": []})
            coll_groups[k]["entries"].append(e)
    ordered_colls = sorted(coll_groups.values(), key=lambda g: g["label"].lower())

    # Tag groups
    tag_groups, untagged = {}, []
    for e in db.entries:
        kws = norm_keywords(e.get("keywords","") or e.get("keyword",""))
        if not kws:
            untagged.append(e)
        else:
            for gkey, label in kws:
                tag_groups.setdefault(gkey, {"label": label, "entries": []})
                tag_groups[gkey]["entries"].append(e)
    ordered_tags = sorted(tag_groups.values(), key=lambda g: g["label"].lower())

    # Build indices
    coll_index_html = ""
    if ordered_colls:
        links = " · ".join(
            f"<a href='#{g['label'].lower().replace(' ', '-').replace('>', '')}'>{html.escape(g['label'])}</a>"
            for g in ordered_colls
        )
        coll_index_html = f"<nav class='tag-index'>{links}</nav>"

    tag_index_html = ""
    if ordered_tags:
        links = " · ".join(
            f"<a href='#{g['label'].lower().replace(' ', '-')}'>{html.escape(g['label'])}</a>"
            for g in ordered_tags
        )
        tag_index_html = f"<nav class='tag-index'>{links}</nav>"

    # Sections
    coll_sections = []
    for g in ordered_colls:
        items = "\n".join(entry_html(e) for e in sorted(g["entries"], key=entry_sort_key))
        coll_sections.append(f"""
<section id="{g['label'].lower().replace(' ', '-').replace('>', '')}" class="tag-section">
  <h2>{html.escape(g['label'])}</h2>
  <ul class="entries">
    {items}
  </ul>
</section>""".strip())

    tag_sections = []
    for g in ordered_tags:
        items = "\n".join(entry_html(e) for e in sorted(g["entries"], key=entry_sort_key))
        tag_sections.append(f"""
<section id="{g['label'].lower().replace(' ', '-')}" class="tag-section">
  <h2>{html.escape(g['label'])}</h2>
  <ul class="entries">
    {items}
  </ul>
</section>""".strip())

    if untagged:
        items = "\n".join(entry_html(e) for e in sorted(untagged, key=entry_sort_key))
        tag_sections.append(f"""
<section id="untagged" class="tag-section">
  <h2>(Untagged)</h2>
  <ul class="entries">
    {items}
  </ul>
</section>""".strip())

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Reference Library</title>
<link rel="stylesheet" href="styles.css" />
</head>
<body>
<main class="container">
  <header class="header">
    <h1>Reference library</h1>
    <div class="meta">Generated from <code>library.bib</code>. Grouped by <strong>collections</strong> and <strong>tags</strong>. Use the search below to filter.</div>
  </header>

  <div class="search">
    <input id="q" type="search" placeholder="Search title, authors, venue, year, tag, or collection…" aria-label="Search references" />
  </div>

  {coll_index_html}
  {"".join(coll_sections)}

  {tag_index_html}
  {"".join(tag_sections)}

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
      entries.forEach(li => li.classList.remove('hidden'));
      sections.forEach(sec => {{
        const anyVisible = Array.from(sec.querySelectorAll('.entry')).some(li => !li.classList.contains('hidden'));
        sec.classList.toggle('hidden', !anyVisible);
      }});
      return;
    }}
    entries.forEach(li => {{
      const hay = (li.getAttribute('data-text') || '').toLowerCase();
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