// src/App.jsx
import React, { useEffect, useState } from "react";
import { Content, Grid, Column, Loading } from "@carbon/react";
import { Outlet } from "react-router-dom";
import HeaderBar from "./components/HeaderBar";
import Footer from "./components/Footer";
import { fetchCollections, fetchItems, buildCollectionPaths } from "./api";
import { fetchNotesIndex, noteUrlForCitekey } from "./notes";

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

function App({ toggleTheme, theme }) {
  const [collections, setCollections] = useState([]);
  const [allEntries, setAllEntries] = useState({}); // { [collectionKey]: EntryObj[] }
  const [counts, setCounts] = useState({});
  const [paths, setPaths] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);

        // Fetch library metadata + notes index in parallel
        const [colls, notesIndex] = await Promise.all([
          fetchCollections(),
          fetchNotesIndex().catch((e) => {
            console.warn("Notes index fetch failed:", e);
            return {
              keys: new Set(),
              dois: new Map(),
              titleYears: new Map(),
              urlByKey: new Map(),
            };
          }),
        ]);

        const {
          keys: noteKeys,
          dois: noteDois,
          titleYears: noteTitleYears,
          urlByKey,
        } = notesIndex;

        const collsData = colls.map((c) => c.data);
        const children = collsData.filter((c) => c.parentCollection);

        const builtPaths = buildCollectionPaths(collsData);
        setPaths(builtPaths);

        const collectionsList = children
          .map((c) => ({ key: c.key, label: builtPaths[c.key] }))
          .sort((a, b) => {
            const numA = parseInt(a.label, 10);
            const numB = parseInt(b.label, 10);
            return (
              (isNaN(numA) ? Infinity : numA) - (isNaN(numB) ? Infinity : numB)
            );
          });
        setCollections(collectionsList);

        const entryMap = {};
        const countMap = {};

        for (let c of children) {
          const items = await fetchItems(c.key);

          const clean = items
            .map((it) => {
              const d = it.data || {};
              const titleRaw = d.title?.trim();
              if (
                !titleRaw ||
                ["PDF", "UNTITLED"].includes(titleRaw.toUpperCase())
              )
                return null;

              // Full creators with roles
              const creators = (d.creators || [])
                .map((cr) => {
                  const firstName = cr.firstName || "";
                  const lastName = cr.lastName || cr.name || "";
                  const full = [firstName, lastName]
                    .filter(Boolean)
                    .join(" ")
                    .trim();
                  return {
                    creatorType: cr.creatorType,
                    firstName,
                    lastName,
                    full,
                  };
                })
                .filter((cr) => cr.lastName || cr.full);

              // Author last names for fast scoring
              const authors = creators
                .filter((cr) => cr.creatorType === "author")
                .map((cr) => (cr.lastName || cr.full).trim())
                .filter(Boolean);

              const year = (d.date || "").split("-")[0] || "";
              const venue =
                d.publicationTitle || d.bookTitle || d.conferenceName || "";
              const itemType = d.itemType || "";
              const tags = (d.tags || []).map((t) => t.tag).filter(Boolean);
              const language = d.language || "";
              const doi = d.DOI || "";
              const url = d.url || "";

              // Determine if this item has notes:
              // 1) DOI match
              let notesCitekey = null;
              if (doi) {
                const nd = normDoi(doi);
                if (nd && noteDois.has(nd)) notesCitekey = noteDois.get(nd);
              }
              // 2) fallback: title+year match
              if (!notesCitekey) {
                const t = norm(titleRaw).replace(/[{}]/g, "").trim();
                const y = String(year || "").trim();
                if (t && y) {
                  const k = `${t}@${y}`;
                  if (noteTitleYears.has(k))
                    notesCitekey = noteTitleYears.get(k);
                }
              }
              // 3) last resort: explicit citekey present in notes index (if your notes index uses Zotero key as citekey)
              if (
                !notesCitekey &&
                d.key &&
                typeof d.key === "string" &&
                noteKeys.has(d.key)
              ) {
                notesCitekey = d.key;
              }

              const hasNotes = Boolean(notesCitekey);
              let notesUrl = null;
              if (hasNotes) {
                const fromIndex = urlByKey.get(notesCitekey);
                notesUrl = fromIndex || noteUrlForCitekey(notesCitekey);
              }

              // Broader searchable text to support phrase queries & analytics
              const searchText = [
                titleRaw,
                creators.map((c) => c.full).join(", "),
                venue,
                year,
                itemType,
                tags.join(", "),
                language,
              ]
                .filter(Boolean)
                .join(" — ");

              return {
                id: d.key || `${titleRaw}-${year}-${c.key}`,
                key: d.key,
                title: titleRaw,
                creators,
                authors,
                year,
                venue,
                itemType,
                tags,
                language,
                doi,
                url,
                collectionKey: c.key,
                collectionLabel: builtPaths[c.key],
                searchText,

                // Notes enrichment
                hasNotes,
                notesCitekey,
                notesUrl,
              };
            })
            .filter(Boolean);

          entryMap[c.key] = clean;
          countMap[c.key] = clean.length;
        }

        setAllEntries(entryMap);
        setCounts(countMap);
      } catch (err) {
        console.error("Error loading data", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const outletContext = {
    theme,
    toggleTheme,
    collections,
    allEntries,
    counts,
    paths,
    loading,
  };

  return (
    <>
      {loading && (
        <div className="app-loading-overlay" role="status" aria-live="polite">
          <Loading active withOverlay={false} />
          <div className="app-loading-text">Loading Zotero data…</div>
        </div>
      )}

      <HeaderBar theme={theme} toggleTheme={toggleTheme} />
      <Content aria-busy={loading}>
        <Grid className="cds--grid cds--grid--narrow">
          <Column lg={12} md={8} sm={4}>
            <Outlet context={outletContext} />
          </Column>
        </Grid>
        <Footer />
      </Content>
    </>
  );
}

export default App;
