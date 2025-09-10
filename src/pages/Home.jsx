// src/pages/Home.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useOutletContext, useSearchParams, Link } from "react-router-dom";
import SearchBox from "../components/SearchBox.jsx";
import PillRow from "../components/PillRow.jsx";
import CollectionSection from "../components/CollectionSection.jsx";

/* Utils */
function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
function highlightHTML(text, query) {
  if (!query?.trim() || !text) return text;
  const re = new RegExp(`(${escapeRegExp(query.trim())})`, "gi");
  return String(text).replace(re, "<mark>$1</mark>");
}

/* Scoring for search relevance */
function scoreEntry(e, q) {
  if (!q) return 0;
  const needle = q.toLowerCase();

  let s = 0;
  for (const a of e.authors || []) {
    const al = a.toLowerCase();
    if (al === needle) s += 100;
    else if (al.startsWith(needle)) s += 70;
    else if (al.includes(needle)) s += 60;
  }
  const tl = (e.title || "").toLowerCase();
  if (tl.includes(needle)) s += 30;

  const vl = (e.venue || "").toLowerCase();
  if (vl.includes(needle)) s += 10;

  if (typeof e.year === "string" && e.year.toLowerCase() === needle) s += 5;

  const sl = (e.searchText || "").toLowerCase();
  if (sl.includes(needle)) s += 8;

  return s;
}

export default function Home() {
  const { collections, allEntries, paths } = useOutletContext();
  const [query, setQuery] = useState("");
  const [activeCollection, setActiveCollection] = useState(null);
  const [searchParams, setSearchParams] = useSearchParams();

  // Deep-link support (collection + q)
  useEffect(() => {
    const col = searchParams.get("collection");
    const q = searchParams.get("q");
    if (col) setActiveCollection(col);
    if (q) setQuery(q);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const next = new URLSearchParams(searchParams);
    if (activeCollection) next.set("collection", activeCollection);
    else next.delete("collection");

    if (query?.trim()) next.set("q", query.trim());
    else next.delete("q");

    setSearchParams(next, { replace: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeCollection, query]);

  /* Flat list for global search */
  const flat = useMemo(() => {
    const out = [];
    for (const key of Object.keys(allEntries)) {
      const arr = allEntries[key] || [];
      for (const e of arr) out.push(e);
    }
    return out;
  }, [allEntries]);

  /* Search results (optionally filtered by active collection) */
  const results = useMemo(() => {
    const q = query.trim();
    if (!q) return [];
    const base = activeCollection
      ? flat.filter((e) => e.collectionKey === activeCollection)
      : flat;

    return base
      .map((e) => ({ e, s: scoreEntry(e, q) }))
      .filter(({ s }) => s > 0)
      .sort((a, b) => b.s - a.s)
      .map(({ e }) => e);
  }, [flat, query, activeCollection]);

  /* Legacy listing when no query: show a chosen collection */
  const legacyEntries = useMemo(() => {
    if (!activeCollection || query.trim()) return [];
    return allEntries[activeCollection] || [];
  }, [activeCollection, allEntries, query]);

  return (
    <>
      <h1 className="section-title" style={{ marginTop: 0 }}>Home</h1>

      <SearchBox
        query={query}
        setQuery={(v) => {
          setQuery(v);
          if (v) setActiveCollection(null); // clear filter when typing
        }}
      />

      {/* SEARCH MODE: results first; each result ends with a collection pill (as a Link) */}
      {query.trim() && (
        <div style={{ marginTop: "1rem" }}>
          <CollectionSection
            title={`${results.length} result${results.length === 1 ? "" : "s"}`}
            entries={results.map((e) => (
              <span key={e.id}>
                <span
                  dangerouslySetInnerHTML={{ __html: highlightHTML(e.title, query) }}
                />
                {" — "}
                <span
                  dangerouslySetInnerHTML={{
                    __html: highlightHTML((e.authors || []).join(", "), query),
                  }}
                />
                {e.year ? `, ${e.year}` : ""}{" "}
                {e.venue ? (
                  <em>
                    {" — "}
                    <span
                      dangerouslySetInnerHTML={{
                        __html: highlightHTML(e.venue, query),
                      }}
                    />
                  </em>
                ) : null}
                {" "}
                <Link
                  className="pill"
                  to={`/collection/${e.collectionKey}${query ? `?q=${encodeURIComponent(query)}` : ""}`}
                  aria-label={`View collection ${e.collectionLabel}`}
                  style={{ marginLeft: "0.5rem" }}
                >
                  {e.collectionLabel}
                </Link>
              </span>
            ))}
          />
        </div>
      )}

      {/* NO-SEARCH MODE: keep original experience */}
      {!query.trim() && (
        <>
          <PillRow
            pills={collections}
            activePill={activeCollection}
            setActivePill={setActiveCollection}
          />

          {activeCollection && (
            <CollectionSection
              title={paths[activeCollection] || "Collection"}
              entries={legacyEntries.map((e) => (
                <span key={e.id}>
                  {e.title} — {(e.authors || []).join(", ")}
                  {e.year ? `, ${e.year}` : ""}{" "}
                  {e.venue ? <em> — {e.venue}</em> : null}
                </span>
              ))}
            />
          )}
        </>
      )}
    </>
  );
}