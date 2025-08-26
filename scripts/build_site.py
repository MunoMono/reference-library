#!/usr/bin/env python3
"""
Build a static HTML page at docs/index.html from library.bib, grouped by:
- Zotero collections (Better BibTeX "Include collections")
- Tags (BibTeX keywords; comma/semicolon separated)

Adds minimal TeX cleanup for labels (e.g., {\textbar} -> |).
Outputs HTML that links to docs/styles.css (no inline CSS for styles, but charts are inlined as SVG).
"""

import re
import html
import unicodedata
from pathlib import Path
import bibtexparser

# chart generator (make sure we can import it when run as a script)
import sys as _sys
_sys.path.append(str(Path(__file__).resolve().parent))
from generate_charts import build_charts

ROOT = Path(__file__).resolve().parents[1]
BIB_PATH = ROOT / "library.bib"
DOCS_DIR = ROOT / "docs"
OUT = DOCS_DIR / "index.html"
STYLES = DOCS_DIR / "styles.css"

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

# ------------ tag color key mapping (server-side) ------------
def canon(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.casefold()
    s = s.replace("–", "-").replace("—", "-").replace("’", "'")
    s = re.sub(r"\s*\|\s*", " | ", s)
    s = re.sub(r"[^a-z0-9|]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

SPECIAL_TAGS_CANON = {
    canon("Theoretical paper"): "theoretical",
    canon("Consciousness-raising paper"): "consciousness-raising",
    canon("Consciousness raising paper"): "consciousness-raising",
    canon("Agenda setting paper"): "agenda-setting",
    canon("Review paper"): "review",
    canon("Position paper"): "position",
    canon("PhD thesis"): "phd-thesis",
}

SPECIAL_PREFIXES = [
    (canon("Data driven |"), "data-driven"),
    (canon("Methods |"), "methods"),
]

def tag_key(label: str) -> str:
    c = canon(label)
    if c in SPECIAL_TAGS_CANON:
        return SPECIAL_TAGS_CANON[c]
    for pref, key in SPECIAL_PREFIXES:
        if c.startswith(pref):
            return key
    return ""

# ------------------------------------------------------------

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

    # Attach data-key for special tags so CSS can recolor them
    tag_spans = []
    for t in tags:
        k = tag_key(t)
        if k:
            tag_spans.append(f"<span class='tag' data-key='{esc(k)}'>{esc(t)}</span>")
        else:
            tag_spans.append(f"<span class='tag'>{esc(t)}</span>")

    tags_html = " ".join(tag_spans) if tag_spans else ""
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

    # ---- generate charts (writes SVGs into docs/) ----
    charts = build_charts(BIB_PATH, DOCS_DIR)
    paper_svg_path = DOCS_DIR / charts["paper_types_svg"]
    coll_svg_path  = DOCS_DIR / charts["collections_svg"]
    paper_svg_inline = paper_svg_path.read_text(encoding="utf-8")
    coll_svg_inline  = coll_svg_path.read_text(encoding="utf-8")

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

    # ---------- HTML ----------
    html_doc = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="color-scheme" content="dark" />
<title>Reference Library</title>
<link rel="stylesheet" href="styles.css?v=6" />
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

  <!-- Charts directly under the search box -->
  <section id="overview" class="tag-section" style="margin-top:1.25rem;">
    <h2>Overview</h2>
    <div class="entries" style="list-style:none; display:grid; gap:1rem;">
      <figure style="margin:0;">{paper_svg_inline}</figure>
      <figure style="margin:0;">{coll_svg_inline}</figure>
    </div>
  </section>

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
  const allSections = Array.from(document.querySelectorAll('.tag-section'));
  // Exclude the overview section from hide/show logic
  const sections = allSections.filter(sec => sec.id !== 'overview');
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