#!/usr/bin/env python3
"""
generate_charts.py — tiny dependency-free viz helpers for reference-library.

Reads a BibTeX file, computes:
  1) Paper Type counts (specific tags/families you defined)
  2) "Collections" = all OTHER tags (i.e., every tag not used for Paper Types)

Writes static SVG charts into the docs/ directory and returns the file names.
"""

from __future__ import annotations
import re
import math
import html
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple
import bibtexparser

# ---------------------------- canonicalization ----------------------------

def canon(s: str) -> str:
    """Canonicalize strings for tolerant matching (case/spacing/punct)."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.casefold()
    s = s.replace("–", "-").replace("—", "-").replace("’", "'")
    s = re.sub(r"\s*\|\s*", " | ", s)      # normalize " | "
    s = re.sub(r"[^a-z0-9|]+", " ", s)     # keep alnum and pipe
    s = re.sub(r"\s+", " ", s).strip()
    return s

# ---------------------------- taxonomy ------------------------------------

# Singles
SINGLES = {
    "Theoretical paper": "Theoretical paper",
    "Consciousness-raising paper": "Consciousness-raising paper",
    "Agenda setting paper": "Agenda setting paper",
    "Review paper": "Review paper",
    "Position paper": "Position paper",
    "PhD thesis": "PhD thesis",
}
SINGLES_CANON = {canon(k): v for k, v in SINGLES.items()}
# Allow variant without hyphen for matching
SINGLES_CANON[canon("Consciousness raising paper")] = "Consciousness-raising paper"

# Families (prefix → family label) — keep for recognition
FAMILIES = [
    ("Data driven |", "Data driven"),
    ("Methods |", "Methods"),
]
FAMILIES_CANON = [(canon(p), label) for p, label in FAMILIES]

# All specific paper-type members we care about
PAPER_TYPE_MEMBERS = {
    "Data driven | meta-study paper",
    "Data driven | artefact paper",
    "Data driven | work-in-progress paper",
    "Methods | method introduction paper",
    "Methods | tutorial paper",
    "Methods | method-mongering paper",
    "Methods | demonstration of concept paper",
}
PAPER_TYPE_MEMBERS_CANON = {canon(x) for x in PAPER_TYPE_MEMBERS}

# ---------------------------- parsing helpers -----------------------------

def clean_tex(s: str) -> str:
    if not s:
        return ""
    s = s.replace(r"{\textbar}", "|").replace(r"\textbar", "|")
    s = s.replace(r"\&", "&")
    s = re.sub(r"[{}]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def norm_keywords(value: str) -> List[str]:
    if not value:
        return []
    raw = re.split(r"[;,]", value)
    return [clean_tex(w.strip()) for w in raw if w.strip()]

# ---------------------------- counting ------------------------------------

def count_paper_types(db) -> Dict[str, int]:
    """Count the requested paper-type tags (the 7 family members + 6 singles)."""
    counts: Dict[str, int] = {
        "Data driven | meta-study paper": 0,
        "Data driven | artefact paper": 0,
        "Data driven | work-in-progress paper": 0,
        "Methods | method introduction paper": 0,
        "Methods | tutorial paper": 0,
        "Methods | method-mongering paper": 0,
        "Methods | demonstration of concept paper": 0,
        "Theoretical paper": 0,
        "Consciousness-raising paper": 0,
        "Agenda setting paper": 0,
        "Review paper": 0,
        "Position paper": 0,
        "PhD thesis": 0,
    }

    # Canon maps for the specific family members
    FAMILY_EXACTS = {
        canon("Data driven | meta-study paper"): "Data driven | meta-study paper",
        canon("Data driven | artefact paper"): "Data driven | artefact paper",
        canon("Data driven | work-in-progress paper"): "Data driven | work-in-progress paper",
        canon("Methods | method introduction paper"): "Methods | method introduction paper",
        canon("Methods | tutorial paper"): "Methods | tutorial paper",
        canon("Methods | method-mongering paper"): "Methods | method-mongering paper",
        canon("Methods | demonstration of concept paper"): "Methods | demonstration of concept paper",
    }

    for e in db.entries:
        tags = norm_keywords(e.get("keywords","") or e.get("keyword",""))
        if not tags:
            continue
        for t in tags:
            c = canon(t)
            # singles
            if c in SINGLES_CANON:
                counts[SINGLES_CANON[c]] += 1
                continue
            # specific family members
            if c in FAMILY_EXACTS:
                counts[FAMILY_EXACTS[c]] += 1

    # Remove zero-counts to keep charts clean
    return {k: v for k, v in counts.items() if v > 0}

def count_other_tags(db) -> Dict[str, int]:
    """
    Count all tags EXCEPT those used for Paper Types (singles + specific family members).
    Result is a dict {label: count}.
    """
    counts: Dict[str, int] = {}
    for e in db.entries:
        tags = norm_keywords(e.get("keywords","") or e.get("keyword",""))
        if not tags:
            continue
        for t in tags:
            c = canon(t)
            if (c in SINGLES_CANON) or (c in PAPER_TYPE_MEMBERS_CANON):
                continue  # skip paper-type tags
            # skip broad family headers like "Data driven |" or "Methods |" if they ever appear alone
            if any(c.startswith(pref) for pref, _ in FAMILIES_CANON):
                # only include if it's not one of our known members; handled above
                pass
            # count the original label
            counts[t] = counts.get(t, 0) + 1
    return counts

# ---------------------------- SVG helpers ---------------------------------

# Carbon-ish palette (dark-friendly). We’ll cycle if needed.
PALETTE = [
    "#78a9ff", "#a7f0ba", "#ffb3b8", "#ffd7a8", "#e8daff", "#b3e6ff",
    "#f1c21b", "#8a3ffc", "#33b1ff", "#fa4d56", "#6fdc8c", "#ff832b",
]

def _escape(s: str) -> str:
    return html.escape(s, quote=True)

def pie_svg(data: List[Tuple[str, int]], title: str, size: int = 420) -> str:
    """Return a simple pie chart SVG (no deps)."""
    total = sum(v for _, v in data) or 1
    cx = cy = size // 2
    r = size * 0.44
    stroke = "#161616"
    bg = "none"

    def polar(a_deg: float):
        rad = math.radians(a_deg)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)

    svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" role="img" aria-label="{_escape(title)}">',
                 f'<title>{_escape(title)}</title>',
                 f'<rect x="0" y="0" width="{size}" height="{size}" fill="{bg}" />']
    a0 = -90.0  # start at top
    for i, (label, value) in enumerate(data):
        frac = value / total
        a1 = a0 + frac * 360.0
        large = 1 if (a1 - a0) % 360 > 180 else 0
        x0, y0 = polar(a0)
        x1, y1 = polar(a1)
        color = PALETTE[i % len(PALETTE)]
        path = f"M {cx} {cy} L {x0:.3f} {y0:.3f} A {r:.3f} {r:.3f} 0 {large} 1 {x1:.3f} {y1:.3f} Z"
        svg_parts.append(f'<path d="{path}" fill="{color}" stroke="{stroke}" stroke-width="0.5"/>')
        a0 = a1

    # legend
    legend_x = size * 0.64
    legend_y = size * 0.12
    line_h = 18
    svg_parts.append(f'<g font-family="IBM Plex Sans, system-ui" font-size="12" fill="#f4f4f4">')
    svg_parts.append(f'<text x="{size*0.06:.0f}" y="{size*0.08:.0f}" font-size="16" font-weight="600">{_escape(title)}</text>')
    for i, (label, value) in enumerate(data):
        y = legend_y + i * line_h
        color = PALETTE[i % len(PALETTE)]
        svg_parts.append(f'<rect x="{legend_x}" y="{y-10}" width="12" height="12" rx="2" fill="{color}"/>')
        svg_parts.append(f'<text x="{legend_x+18}" y="{y}" dominant-baseline="middle">{_escape(label)} ({value})</text>')
    svg_parts.append('</g></svg>')
    return "".join(svg_parts)

def hbar_svg(data: List[Tuple[str, int]], title: str, width: int = 720, bar_h: int = 22, gap: int = 8) -> str:
    """Return a horizontal bar chart SVG (no deps)."""
    n = len(data)
    height = 90 + n * (bar_h + gap)
    maxv = max((v for _, v in data), default=1) or 1
    left = 180
    right = 24
    top = 48
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{_escape(title)}">',
           f'<title>{_escape(title)}</title>',
           f'<rect x="0" y="0" width="{width}" height="{height}" fill="none" />',
           f'<g font-family="IBM Plex Sans, system-ui" fill="#f4f4f4">']
    svg.append(f'<text x="24" y="28" font-size="18" font-weight="600">{_escape(title)}</text>')
    for i, (label, value) in enumerate(data):
        y = top + i * (bar_h + gap)
        w = (width - left - right) * (value / maxv)
        color = PALETTE[i % len(PALETTE)]
        svg.append(f'<text x="24" y="{y + bar_h*0.7:.1f}" font-size="12">{_escape(label)}</text>')
        svg.append(f'<rect x="{left}" y="{y}" width="{w:.1f}" height="{bar_h}" rx="4" fill="{color}"/>')
        svg.append(f'<text x="{left + w + 6:.1f}" y="{y + bar_h*0.7:.1f}" font-size="12">{value}</text>')
    svg.append('</g></svg>')
    return "".join(svg)

# ---------------------------- orchestrator --------------------------------

def build_charts(bib_path: Path, out_dir: Path) -> Dict[str, str]:
    """Generate charts and write SVGs into out_dir. Return dict with filenames."""
    with open(bib_path, "r", encoding="utf-8") as f:
        db = bibtexparser.load(f)

    # 1) Paper types
    pt_counts = count_paper_types(db)
    paper_types = sorted(pt_counts.items(), key=lambda kv: (-kv[1], kv[0]))

    # 2) "Collections" = all other tags (top 12 + "Other")
    other_counts = count_other_tags(db)
    other_sorted = sorted(other_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(other_sorted) > 12:
        head = other_sorted[:12]
        other_sum = sum(v for _, v in other_sorted[12:])
        head.append(("Other", other_sum))
        collections = head
    else:
        collections = other_sorted

    # choose chart types
    paper_svg = pie_svg(paper_types, "Paper types") if len(paper_types) <= 9 else hbar_svg(paper_types, "Paper types")
    coll_svg = hbar_svg(collections, "Collections")

    out_dir.mkdir(parents=True, exist_ok=True)
    paper_file = out_dir / "chart_paper_types.svg"
    coll_file = out_dir / "chart_collections.svg"
    paper_file.write_text(paper_svg, encoding="utf-8")
    coll_file.write_text(coll_svg, encoding="utf-8")

    return {
        "paper_types_svg": paper_file.name,
        "collections_svg": coll_file.name,
    }

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    charts = build_charts(root / "library.bib", root / "docs")
    print("Wrote:", charts)