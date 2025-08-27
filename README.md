# Reference Library

[![Deploy Reference Library Site](https://github.com/MunoMono/reference-library/actions/workflows/deploy.yml/badge.svg)](https://github.com/MunoMono/reference-library/actions/workflows/deploy.yml)

A live, browsable reference library powered by the **Zotero API**.  
The site renders all child collections as interactive pills, shows their entries, and visualises counts with a clickable chart.

Live version: [https://munomono.github.io/reference-library/](https://munomono.github.io/reference-library/)

---

## 📚 About

This repository connects directly to my Zotero library and publishes an **interactive reference library site** via GitHub Pages.

- **Data source**: Zotero API (all collections + items)  
- **Viewer**: static site in `docs/index.html` with:
  - pills for each child collection (55 total),
  - breadcrumb labels for hierarchy,
  - dynamically rendered items,
  - a scrollable bar chart of counts per sub-collection.  
- **Styling**: [IBM Carbon Design](https://carbondesignsystem.com/) inspired CSS (`docs/styles.css`)  
- **Build process**: `scripts/build_site.py` fetches data from Zotero and generates the static site  
- **Deployment**: automated with GitHub Actions  

---

## 🚀 Usage

- **View online**:  
  [https://munomono.github.io/reference-library/](https://munomono.github.io/reference-library/)

- **Build locally**:

```bash
git clone https://github.com/MunoMono/reference-library.git
cd reference-library
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/build_site.py
open docs/index.html
```

---

## 🧩 Features

- **Pills navigation**  
  All Zotero child collections appear as pills, sorted by numeric prefix (e.g. `0 Backlog` → `12 Not applicable`).

- **Breadcrumbs**  
  Each pill shows its full path in the collection hierarchy (e.g. `4 Archival Research | emerging > AI/ML in archives`).

- **Entries view**  
  On clicking a pill, entries are fetched and displayed (cleaned of placeholder items like `PDF`).

- **Interactive chart**  
  A horizontal scrollable bar chart visualises the number of entries per sub-collection.  
  Clicking a bar activates the corresponding pill and scrolls to the section.

- **Responsive design**  
  Chart and pills adapt for mobile with horizontal scrolling.

---

## 🐍 Development

Key scripts:

- `scripts/build_site.py` — main builder, fetches Zotero collections + items and generates `docs/index.html`  
- `docs/styles.css` — Carbon-inspired site styling  
- `scripts/list_collections.sh` / `scripts/list_counts.sh` — helpers for testing API responses  

---

## 🔖 License

- Bibliographic **data** is licensed under [CC BY 4.0](./LICENSE-CC-BY-4.0.txt).  
- Repository configuration, scripts, and documentation are licensed under [MIT](./LICENSE).  
