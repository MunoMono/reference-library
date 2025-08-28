# Reference Library

[![Deploy Reference Library Site](https://github.com/MunoMono/reference-library/actions/workflows/deploy.yml/badge.svg)](https://github.com/MunoMono/reference-library/actions/workflows/deploy.yml)

A live, browsable **reference library** powered by the **Zotero API**, built with **React, Vite, and IBM Carbon Design System**.  
It renders Zotero collections as interactive pills, visualises counts in a chart, and provides live search across both collections and entries.

Live version: [https://munomono.github.io/reference-library/](https://munomono.github.io/reference-library/)

---

## 📚 About

This repository connects directly to my Zotero library and publishes an **interactive reference library site** via GitHub Pages.

- **Data source**: Zotero API (collections + items)  
- **Framework**: React + Vite  
- **UI**: IBM Carbon Design System (`@carbon/react`, `@carbon/styles`)  
- **Features**:
  - Pills navigation with numeric ordering (`0 Backlog` → `12 Not applicable`)  
  - Parent > Child breadcrumbs in pill labels  
  - Clean entry rendering (title, authors, year, venue)  
  - Search/filter across both collection titles *and* entries (with keyword highlighting)  
  - Interactive bar chart (clickable → activates pill)  
  - Light/dark theme toggle (Carbon g90 + white theme override)  
  - Responsive Carbon grid layout with proper margins  
  - Footer with auto-updating “Last updated dd mmm yyyy”  

---

## 🚀 Usage

- **View online**:  
  [https://munomono.github.io/reference-library/](https://munomono.github.io/reference-library/)

- **Run locally**:

```bash
git clone https://github.com/MunoMono/reference-library.git
cd reference-library
npm install
npm run dev
```

- **Build for production**:

```bash
npm run build
npm run preview
```

Deployment is automated via GitHub Actions → GitHub Pages.

---

## 🧩 Features

- **Pills navigation**  
  Zotero child collections appear as pills, ordered numerically by prefix (e.g. `0 Backlog` → `12 Not applicable`).

- **Breadcrumbs**  
  Pills show their full collection hierarchy (`5 Theoretical framework → Critical theory`).

- **Entries view**  
  Clicking a pill displays the cleaned Zotero items (ignores placeholders like `PDF`, `Untitled`).  

- **Search & Highlight**  
  Filter pills *and* entries by keywords. Matches inside entries are highlighted (e.g., author surname).

- **Interactive chart**  
  A horizontal bar chart visualises entry counts per sub-collection. Clicking a bar activates the corresponding pill.

- **Theme toggle**  
  Light/dark mode switch (Carbon g90 theme vs light).

- **Responsive grid**  
  All content sits within a Carbon grid, giving consistent margins like the IBM Design System site.

- **Footer**  
  Shows a small “Last updated” date stamp at bottom-right.

---

## 🛠 Development

Key source files:

- `src/App.jsx` — main application logic  
- `src/components/` — modular components (HeaderBar, PillRow, SearchBox, EntriesChart, Footer, etc.)  
- `src/index.scss` — Carbon theme overrides + custom styling  

Run locally with:

```bash
npm run dev
```

---

## 🔖 License

- Bibliographic **data** is licensed under [CC BY 4.0](./LICENSE-CC-BY-4.0.txt).  
- Application code, configuration, and documentation are licensed under [MIT](./LICENSE).  
