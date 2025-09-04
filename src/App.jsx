import React, { useEffect, useState } from "react";
import { Content, Grid, Column, Loading } from "@carbon/react";
import HeaderBar from "./components/HeaderBar";
import PillRow from "./components/PillRow";
import SearchBox from "./components/SearchBox";
import EntriesChart from "./components/EntriesChart";
import CollectionSection from "./components/CollectionSection";
import Footer from "./components/Footer";
import { fetchCollections, fetchItems, buildCollectionPaths } from "./api";

function App({ toggleTheme, theme }) {
  const [collections, setCollections] = useState([]);
  const [activePill, setActivePill] = useState(null);
  const [entries, setEntries] = useState([]);
  const [allEntries, setAllEntries] = useState({});
  const [query, setQuery] = useState("");
  const [counts, setCounts] = useState({});
  const [paths, setPaths] = useState({});
  const [loading, setLoading] = useState(true); // ← NEW

  // Load collections + all entries once
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true); // ← NEW
        const colls = await fetchCollections();
        const collsData = colls.map((c) => c.data);
        const children = collsData.filter((c) => c.parentCollection);

        const builtPaths = buildCollectionPaths(collsData);
        setPaths(builtPaths);

        const collectionsList = children
          .map((c) => ({
            key: c.key,
            label: builtPaths[c.key],
          }))
          .sort((a, b) => {
            const numA = parseInt(a.label, 10);
            const numB = parseInt(b.label, 10);
            return (
              (isNaN(numA) ? Infinity : numA) - (isNaN(numB) ? Infinity : numB)
            );
          });

        setCollections(collectionsList);

        // Fetch all items for search and counts
        const entryMap = {};
        const countMap = {};
        for (let c of children) {
          const items = await fetchItems(c.key);
          const clean = items
            .map((it) => {
              const d = it.data;
              const title = d.title?.trim();
              if (!title || ["PDF", "UNTITLED"].includes(title.toUpperCase())) {
                return null;
              }
              const authors = (d.creators || [])
                .filter((cr) => cr.creatorType === "author")
                .map((cr) => cr.lastName)
                .join(", ");
              const year = (d.date || "").split("-")[0];
              const venue =
                d.publicationTitle || d.bookTitle || d.conferenceName || "";
              return [title, authors, year, venue].filter(Boolean).join(" — ");
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
        setLoading(false); // ← NEW
      }
    }
    loadData();
  }, []);

  // When pill clicked, load its entries
  useEffect(() => {
    if (activePill) {
      setEntries(allEntries[activePill] || []);
    } else {
      setEntries([]);
    }
  }, [activePill, allEntries]);

  // Helper: highlight matches
  function highlight(text, q) {
    if (!q) return text;
    const regex = new RegExp(`(${q})`, "gi");
    return text.replace(regex, "<mark>$1</mark>");
  }

  // Filter pills: by label OR by entry content
  const filteredCollections = collections.filter((c) => {
    const q = query.toLowerCase();
    const labelMatch = c.label.toLowerCase().includes(q);
    const entryMatch = (allEntries[c.key] || []).some((e) =>
      e.toLowerCase().includes(q)
    );
    return labelMatch || entryMatch;
  });

  // Filter entries if pill active
  const filteredEntries = activePill
    ? (allEntries[activePill] || []).filter((e) =>
        e.toLowerCase().includes(query.toLowerCase())
      )
    : [];

  const chartData = collections.map((c) => ({
    label: c.label,
    key: c.key,
    value: counts[c.key] || 0,
  }));

  return (
    <>
      {/* Full-page overlay spinner while initial Zotero fetch is in-flight */}
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
            <SearchBox query={query} setQuery={setQuery} />

            <PillRow
              pills={filteredCollections}
              activePill={activePill}
              setActivePill={setActivePill}
            />

            {activePill && (
              <CollectionSection
                title={paths[activePill] || "Collection"}
                entries={filteredEntries.map((e, i) => (
                  <span
                    key={i}
                    dangerouslySetInnerHTML={{
                      __html: highlight(e, query),
                    }}
                  />
                ))}
              />
            )}

            <EntriesChart data={chartData} onBarClick={setActivePill} />
          </Column>
        </Grid>
        <Footer />
      </Content>
    </>
  );
}

export default App;
