#!/usr/bin/env python3
"""
Reference library with:
- Pills sorted by numeric prefix (children only)
- Items rendered per sub-collection
- Scrollable horizontal bar chart (all collections, including 0 entries)
- Chart bars clickable -> activate pill + scroll
"""

import html
import re
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
    url = f"{API}/collections/{coll_key}/items?limit=200"
    resp = requests.get(url, headers={"Zotero-API-Key": API_KEY})
    resp.raise_for_status()
    return resp.json()


# ---------------- HTML helpers ----------------
def item_html(item):
    d = item.get("data", {})
    title = d.get("title")
    if not title or title.strip().upper() in ["PDF", "UNTITLED"]:
        return ""

    creators = d.get("creators", [])
    authors = ", ".join(
        c.get("lastName", "") for c in creators if c.get("creatorType") == "author"
    )
    year = (d.get("date") or "").split("-")[0]
    venue = (
        d.get("publicationTitle")
        or d.get("bookTitle")
        or d.get("conferenceName")
        or ""
    )
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

    return f"<li>– {html.escape(meta)}{' · ' + ' · '.join(links) if links else ''}</li>"


def sort_key(label: str):
    m = re.match(r"^(\d+)", label)
    if m:
        return (int(m.group(1)), label.lower())
    return (9999, label.lower())


# ---------------- Main builder ----------------
def build():
    colls = fetch_collections()
    colls_data = [c["data"] for c in colls]
    paths = build_collection_paths(colls_data)

    # all collections (for chart + counts)
    all_sorted = sorted(colls_data, key=lambda c: sort_key(paths[c["key"]]))

    # children only (for pills + sections)
    children = [c for c in colls_data if c.get("parentCollection")]
    children_sorted = sorted(children, key=lambda c: sort_key(paths[c["key"]]))

    # Pills
    pills_html = "\n".join(
        f'<button class="pill" data-target="{c["key"]}" data-label="{html.escape(paths[c["key"]])}">'
        f'{html.escape(paths[c["key"]])}'
        f'</button>'
        for c in children_sorted
    )

    # Sections + counts
    sections_html = ""
    counts = {paths[c["key"]]: 0 for c in all_sorted}  # initialise all collections

    for c in children_sorted:  # only children have sections
        key = c["key"]
        items = fetch_items(key)
        entries = [item_html(it) for it in items if item_html(it)]
        counts[paths[key]] = len(entries)

        items_html = "\n".join(entries)
        sections_html += f"""
<section id='{key}' class='coll-section hidden'>
  <h2>{html.escape(paths[key])}</h2>
  <ul>{items_html}</ul>
</section>
"""

    # Chart data (all collections, sorted)
    chart_data = [{"label": k, "value": v} for k, v in counts.items()]
    chart_data.sort(key=lambda d: sort_key(d["label"]))

    # Full HTML
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Reference library</title>
<link rel="stylesheet" href="styles.css" />
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
<h1>Reference library</h1>
<div class="pill-row">{pills_html}</div>
{sections_html}

<section id="overview">
  <h2>Entries per sub-collection</h2>
  <div class="chart-scroll">
    <div class="chart-container">
      <canvas id="barChart"></canvas>
    </div>
  </div>
</section>

<script>
const pills = document.querySelectorAll('.pill');
const sections = document.querySelectorAll('.coll-section');
pills.forEach(p => {{
  p.addEventListener('click', () => {{
    pills.forEach(x => x.classList.remove('active'));
    p.classList.add('active');
    sections.forEach(sec => sec.classList.add('hidden'));
    const show = document.getElementById(p.dataset.target);
    if (show) {{
      show.classList.remove('hidden');
      show.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}
  }});
}});
if (pills.length) pills[0].click();

const ctx = document.getElementById('barChart').getContext('2d');
const data = {chart_data};
const chart = new Chart(ctx, {{
  type: 'bar',
  data: {{
    labels: data.map(d => d.label),
    datasets: [{{
      label: 'Entries',
      data: data.map(d => d.value),
      backgroundColor: '#0f62fe'
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }}
    }},
    scales: {{
      x: {{ grid: {{ color: '#393939' }}, ticks: {{ color: '#f4f4f4' }} }},
      y: {{ grid: {{ color: '#393939' }}, ticks: {{ color: '#f4f4f4' }} }}
    }},
    onClick: (e, elements) => {{
      if (elements.length > 0) {{
        const index = elements[0].index;
        const label = chart.data.labels[index];
        const pill = Array.from(pills).find(p => p.dataset.label === label);
        if (pill) pill.click();
      }}
    }}
  }}
}});
</script>
</body>
</html>"""

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"Wrote Reference library with clickable chart to {OUT}")


if __name__ == "__main__":
    build()