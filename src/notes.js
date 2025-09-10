// src/notes.js

export const NOTES_INDEX_URL =
  "https://munomono.github.io/reading-notes/docs/index.json";

// ---------- helpers ----------
const norm = (s) =>
  String(s || "")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();

const normDoi = (doi) =>
  norm(doi)
    .replace(/^https?:\/\/(dx\.)?doi\.org\//, "")
    .replace(/^doi:/, "")
    .trim();

/** extract last path segment, with or without .html/.md (case-insensitive) */
function citekeyFromPath(p) {
  if (!p) return null;
  const str = String(p).trim();
  const noSlash = str.endsWith("/") ? str.slice(0, -1) : str;
  const seg = noSlash.split("/").pop() || "";
  return seg.replace(/\.(html?|md)$/i, "");
}

/** flatten any reasonable index.json shape into an array of rows */
function flattenIndexJson(data) {
  if (!data) return [];
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.entries)) return data.entries;          // ← your repo
  if (Array.isArray(data.items)) return data.items;

  // object grouped by letters: { A:[...], B:[...] }
  const keys = Object.keys(data);
  if (keys.length && keys.every((k) => Array.isArray(data[k]))) {
    return keys.flatMap((k) => data[k]);
  }
  return [];
}

/** build a URL like /reading-notes/docs/{Letter}/{slugOrKey} (no .html) */
function buildUrlFromLetterSlug(letter, slug, indexUrl = NOTES_INDEX_URL) {
  try {
    const base = new URL(indexUrl);
    const L = (letter || slug?.[0] || "X").toString().charAt(0).toUpperCase();
    const s = slug || "unknown";
    return new URL(`/reading-notes/docs/${L}/${s}`, base).toString();
  } catch {
    const L = (letter || slug?.[0] || "X").toString().charAt(0).toUpperCase();
    const s = slug || "unknown";
    return `https://munomono.github.io/reading-notes/docs/${L}/${s}`;
  }
}

// ---------- main ----------
/**
 * Returns:
 *  {
 *    keys: Set<string>,
 *    dois: Map<normalizedDoi, citekey>,
 *    titleYears: Map<normalizedTitle + "@" + year, citekey>,
 *    urlByKey: Map<citekey, absoluteUrl>
 *  }
 */
export async function fetchNotesIndex(indexUrl = NOTES_INDEX_URL) {
  const res = await fetch(indexUrl, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error(`Failed to fetch ${indexUrl}: HTTP ${res.status}`);
  const data = await res.json();

  const rows = flattenIndexJson(data);
  const base = new URL(indexUrl);

  const keys = new Set();
  const dois = new Map();
  const titleYears = new Map();
  const urlByKey = new Map();

  for (const r of rows) {
    // your fields from the screenshot:
    // { letter, slug, path, title, authors, year, journal, doi, url, citation_key, ... }
    const letter = r.letter || r.letterCode || "";
    const slug = r.slug || r.citation_key || r.key || r.id || null;

    // if there’s an explicit link, extract citekey from it as a fallback
    const link = r.href ?? r.url ?? r.path ?? null;
    const citeFromLink = citekeyFromPath(link);
    const candidate = String(slug || citeFromLink || "").trim();
    if (!candidate) continue;

    const citekey = candidate;
    keys.add(citekey);

    // build absolute URL preference: explicit link → derived from letter/slug
    let absUrl = null;
    if (link) {
      try {
        absUrl = new URL(link, base).toString();
      } catch {
        absUrl = null;
      }
    }
    if (!absUrl) {
      absUrl = buildUrlFromLetterSlug(letter, citekey, indexUrl);
    }
    urlByKey.set(citekey, absUrl);

    // DOI (normalize if present)
    if (r.doi) {
      const nd = normDoi(r.doi);
      if (nd) dois.set(nd, citekey);
    }

    // Title + Year (normalize)
    const titleRaw = r.title ?? r.displayTitle ?? r.name ?? r.label ?? "";
    const yearRaw = r.year ?? r.date ?? r.published ?? "";
    const t = norm(String(titleRaw).replace(/[{}]/g, ""));
    const y = String(yearRaw || "").match(/\d{4}/)?.[0] || ""; // pull first 4-digit year
    if (t && y) titleYears.set(`${t}@${y}`, citekey);
  }

  // --- DEBUG LOGGING ---
  console.groupCollapsed("📘 Notes index debug");
  console.log("Total rows parsed:", rows.length);
  console.log("First 5 rows raw:", rows.slice(0, 5));
  console.log("Citekeys extracted:", Array.from(keys).slice(0, 10));
  console.log("DOIs mapped:", Array.from(dois.entries()).slice(0, 10));
  console.log("Title+Year mapped:", Array.from(titleYears.entries()).slice(0, 10));
  console.log("URL by key:", Array.from(urlByKey.entries()).slice(0, 10));
  console.groupEnd();

  return { keys, dois, titleYears, urlByKey };
}

/** Fallback URL if needed (kept for completeness) */
export function noteUrlForCitekey(citekey, indexUrl = NOTES_INDEX_URL) {
  return buildUrlFromLetterSlug(citekey?.[0] || "X", citekey, indexUrl);
}