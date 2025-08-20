# Reference Library

[![Deploy Reference Library Site](https://github.com/MunoMono/reference-library/actions/workflows/deploy.yml/badge.svg)](https://github.com/MunoMono/reference-library/actions/workflows/deploy.yml)

A public export of my complete reference library, maintained in **BibTeX** format and viewable online via GitHub Pages.

Live version: [https://munomono.github.io/reference-library/review.html](https://munomono.github.io/reference-library/review.html)

---

## 📚 About

This repository contains the full set of references collected for my research projects.  
It functions as a **reference library**, not just a bibliography for a single paper.  

- **Format**: [BibTeX](https://en.wikipedia.org/wiki/BibTeX) (`library.bib`)  
- **Viewer**: static site generated at `docs/index.html`  
- **Build process**: `scripts/build_site.py` converts `library.bib` → `docs/index.html`  
- **Automation**: a GitHub Action builds & deploys the site on every push  
- **Citation metadata**: see [`CITATION.cff`](./CITATION.cff)

---

## 🚀 Usage

- **Clone or download** this repo to use the `library.bib` file in your own LaTeX, Pandoc, or reference-manager workflow.
- **View online**: the full library is browsable at:

```
https://munomono.github.io/reference-library/
```

---

## 🐍 Development

To build the site locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_site.py
open docs/index.html
```

---

## 🔖 License

- Bibliographic **data** (`library.bib`) is licensed under [CC BY 4.0](./LICENSE-CC-BY-4.0.txt).  
- Repository configuration, scripts, and documentation are licensed under [MIT](./LICENSE).  

---

## ✨ Description

**Reference Library** is a living, version-controlled collection of references exported from my personal research manager.  
It is intended as a **shared dataset**:  
- transparent and easy to reuse,  
- citable via DOI (when connected with Zenodo),  
- and always available in a simple, open format.
