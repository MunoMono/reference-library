#!/usr/bin/env python3
"""
Reference library with:
- Pills sorted by numeric prefix
- Items rendered per sub-collection
- Scrollable vertical bar chart (static data from list_breadcrumbs.sh)
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

    children = [c["data"] for c in colls if c["data"].get("parentCollection")]
    children_sorted = sorted(children, key=lambda c: sort_key(paths[c["key"]]))

    # Pills
    pills_html = "\n".join(
        f'<button class="pill" data-target="{c["key"]}" data-label="{html.escape(paths[c["key"]])}">'
        f'{html.escape(paths[c["key"]])}'
        f'</button>'
        for c in children_sorted
    )

    # Sections
    sections_html = ""
    for c in children_sorted:
        key = c["key"]
        items = fetch_items(key)
        entries = [item_html(it) for it in items if item_html(it)]
        items_html = "\n".join(entries)
        sections_html += f"""
<section id='{key}' class='coll-section hidden'>
  <h2>{html.escape(paths[key])}</h2>
  <ul>{items_html}</ul>
</section>
"""

    # Hardcoded chart data (from list_breadcrumbs.sh run)
    chart_data = [
        {"label": "Taxonomic theory", "value": 21},
        {"label": "★ Core", "value": 14},
        {"label": "Design Studies", "value": 0},
        {"label": "Visible Language", "value": 0},
        {"label": "Admin / misc.", "value": 0},
        {"label": "Off-topic", "value": 2},
        {"label": "12 Not applicable", "value": 0},
        {"label": "Others", "value": 3},
        {"label": "Design Issues", "value": 5},
        {"label": "She Ji", "value": 7},
        {"label": "11 Context", "value": 0},
        {"label": "Other institutions", "value": 0},
        {"label": "RMIT", "value": 0},
        {"label": "MIT", "value": 1},
        {"label": "RCA", "value": 1},
        {"label": "10 Thesis", "value": 2},
        {"label": "Open access and infrastructures", "value": 0},
        {"label": "Classification and power", "value": 1},
        {"label": "Information ethics", "value": 0},
        {"label": "9 Critical librarianship", "value": 1},
        {"label": "Knowledge organisation theory", "value": 1},
        {"label": "Library / archival taxonomies", "value": 0},
        {"label": "Design methods taxonomies", "value": 0},
        {"label": "8 Taxonomy", "value": 0},
        {"label": "Applications in design and archives", "value": 1},
        {"label": "Academic CS papers", "value": 4},
        {"label": "7 AI/ML/CE/RAG/NLP", "value": 0},
        {"label": "Hybrid / systems approaches (decision-support, prototyping)", "value": 1},
        {"label": "Quantitative (stats, modelling, surveys)", "value": 0},
        {"label": "Qualitative (interviews, ethnography, discourse analysis)", "value": 1},
        {"label": "6 Methodological toolkit", "value": 0},
        {"label": "Design research paradigms", "value": 3},
        {"label": "Critical theory", "value": 2},
        {"label": "Interpretivism", "value": 3},
        {"label": "5 Theoretical framework", "value": 1},
        {"label": "AI/ML in archives (humanities perspective)", "value": 3},
        {"label": "Contemporary archival theory", "value": 3},
        {"label": "Digital humanities", "value": 3},
        {"label": "4 Archival Research | emerging", "value": 0},
        {"label": "Historiography and philosophy of archives", "value": 1},
        {"label": "3 Archival Research | foundational", "value": 0},
        {"label": "Related archives (V&A, Design Council, BL)", "value": 0},
        {"label": "Secondary analysis", "value": 0},
        {"label": "Primary documents", "value": 0},
        {"label": "2 DDR archive", "value": 0},
        {"label": "Secondary commentary", "value": 2},
        {"label": "Articles and papers", "value": 3},
        {"label": "Monographs and thesis", "value": 4},
        {"label": "1 Archer", "value": 0},
        {"label": "Grey literature", "value": 0},
        {"label": "Books", "value": 0},
        {"label": "Journal articles", "value": 0},
        {"label": "☆ Low priority", "value": 0},
        {"label": "★High priority", "value": 1},
        {"label": "0 Backlog (to be read)", "value": 8},
    ]
    chart_data.sort(key=lambda d: sort_key(d["label"]))

    # Chart height = 25px per bar
    chart_height = len(chart_data) * 25

    # Full HTML
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Reference library</title>
<link rel="stylesheet" href="styles.css" />
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  .chart-scroll {{
    max-height: 600px;
    overflow-y: auto;
    border: 1px solid #393939;
    padding: 0.5rem;
  }}
  .chart-container {{
    position: relative;
    height: {chart_height}px;
    min-width: 800px;
  }}
</style>
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
new Chart(ctx, {{
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
    }}
  }}
}});
</script>
</body>
</html>"""

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"Wrote Reference library with scrollable chart to {OUT}")


if __name__ == "__main__":
    build()