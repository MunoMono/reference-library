#!/usr/bin/env python3
"""
Build an HTML page of Zotero child collections with breadcrumb labels
and their items rendered below when a pill is clicked.
"""

import html
import requests
from pathlib import Path

# --- Config ---
USER_ID = "3436801"
API_KEY = "Trlijv6r9XeMU6QF1TcI1YaB"
API = f"https://api.zotero.org/users/{USER_ID}"

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
OUT = DOCS_DIR / "index.html"


# ---------------- API helpers ----------------
def fetch_collections():
    url = f"{API}/collections?limit=200"
    resp = requests.get(url, headers={"Zotero-API-Key": API_KEY})
    resp.raise_for_status()
    return resp.json()


def build_collection_paths(colls_data):
    """Return dict of key → full_path string, given a list of .data dicts"""
    lookup = {c["key"]: c for c in colls_data}

    def path(c):
        parts = [c["name"]]
        parent = c.get("parentCollection")
        while parent and parent in lookup:
            parent_coll = lookup[parent]
            parts.insert(0, parent_coll["name"])
            parent = parent_coll.get("parentCollection")
        return " > ".join(parts)

    return {k: path(v) for k, v in lookup.items()}


def fetch_items(coll_key):
    url = f"{API}/collections/{coll_key}/items?limit=100"
    resp = requests.get(url, headers={"Zotero-API-Key": API_KEY})
    resp.raise_for_status()
    return resp.json()


# ---------------- HTML helpers ----------------
def item_html(item):
    d = item.get("data", {})
    title = d.get("title", "(untitled)")
    creators = d.get("creators", [])
    authors = ", ".join(
        c.get("lastName", "") for c in creators if c.get("creatorType") == "author"
    )
    year = (d.get("date") or "").split("-")[0]
    venue = d.get("publicationTitle") or d.get("bookTitle") or d.get("conferenceName") or ""
    doi = d.get("DOI")
    url = d.get("url")

    meta_parts = [title]
    if authors:
        meta_parts.append(authors)
    if year:
        meta_parts.append(year)
    if venue:
        meta_parts.append(venue)
    meta = " — ".join(meta_parts)

    links = []
    if doi:
        links.append(f"<a href='https://doi.org/{html.escape(doi)}'>DOI</a>")
    if url:
        links.append(f"<a href='{html.escape(url)}'>Link</a>")

    return f"<li>{html.escape(meta)}{' · ' + ' · '.join(links) if links else ''}</li>"


# ---------------- Main builder ----------------
def build():
    colls = fetch_collections()
    colls_data = [c["data"] for c in colls]
    paths = build_collection_paths(colls_data)

    # only child collections
    children = [c["data"] for c in colls if c["data"].get("parentCollection")]

    # pills
    pills_html = "\n".join(
        f'<button class="pill" data-target="{c["key"]}">'
        f'{html.escape(paths[c["key"]])}'
        f'</button>'
        for c in children
    )

    # sections with items
    sections_html = ""
    for c in children:
        key = c["key"]
        items = fetch_items(key)
        items_html = "\n".join(item_html(it) for it in items)
        sections_html += f"""
<section id='{key}' class='coll-section hidden'>
  <h2>{html.escape(paths[key])}</h2>
  <ul>{items_html}</ul>
</section>
"""

    # full HTML
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Zotero Child Collections</title>
<style>
body {{ font-family: sans-serif; background:#111; color:#eee; }}
h1 {{ font-weight: normal; }}
.pill-row {{ margin:1rem 0; display:flex; flex-wrap:wrap; gap:.5rem; }}
.pill {{ padding:.5rem 1rem; border:none; border-radius:999px; cursor:pointer; background:#333; color:#eee; }}
.pill.active {{ background:#06c; color:#fff; }}
.hidden {{ display:none; }}
a {{ color:#6cf; }}
</style>
</head>
<body>
<h1>Child Collections</h1>
<div class="pill-row">{pills_html}</div>
{sections_html}
<script>
const pills = document.querySelectorAll('.pill');
const sections = document.querySelectorAll('.coll-section');
pills.forEach(p => {{
  p.addEventListener('click', () => {{
    pills.forEach(x => x.classList.remove('active'));
    p.classList.add('active');
    sections.forEach(sec => sec.classList.add('hidden'));
    const show = document.getElementById(p.dataset.target);
    if (show) show.classList.remove('hidden');
  }});
}});
if (pills.length) pills[0].click();
</script>
</body>
</html>"""

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"Wrote child collections with items to {OUT}")


if __name__ == "__main__":
    build()