import React, { useEffect, useState } from "react";
import { Content, Grid, Column, Theme } from "@carbon/react";
import HeaderBar from "./components/HeaderBar";
import PillRow from "./components/PillRow";
import SearchBox from "./components/SearchBox";
import EntriesChart from "./components/EntriesChart";
import CollectionSection from "./components/CollectionSection";
import { fetchCollections, fetchItems } from "./api";

function App() {
  const [collections, setCollections] = useState([]);
  const [activePill, setActivePill] = useState(null);
  const [entries, setEntries] = useState([]);
  const [query, setQuery] = useState("");
  const [counts, setCounts] = useState({});

  // Utility: format + filter entries
  const formatEntries = (items) =>
    items
      .map((it) => {
        const d = it.data;
        const title = d.title?.trim();
        if (!title || ["PDF", "UNTITLED"].includes(title.toUpperCase())) {
          return null; // skip attachments
        }

        const authors = (d.creators || [])
          .filter((c) => c.creatorType === "author")
          .map((c) => c.lastName)
          .join(", ");

        const year = (d.date || "").split("-")[0];
        const venue =
          d.publicationTitle || d.bookTitle || d.conferenceName || "";

        return [title, authors, year, venue].filter(Boolean).join(" — ");
      })
      .filter(Boolean);

  // Fetch collections and counts
  useEffect(() => {
    async function loadData() {
      try {
        const colls = await fetchCollections();
        const children = colls.filter((c) => c.data.parentCollection);

        setCollections(
          children.map((c) => ({
            key: c.data.key,
            label: c.data.name,
          }))
        );

        const countMap = {};
        for (let c of children) {
          const items = await fetchItems(c.data.key);
          const valid = formatEntries(items);
          countMap[c.data.key] = valid.length;
        }
        setCounts(countMap);
      } catch (err) {
        console.error("Error loading data", err);
      }
    }
    loadData();
  }, []);

  // Fetch entries for active pill
  useEffect(() => {
    async function loadEntries() {
      if (activePill) {
        const items = await fetchItems(activePill);
        setEntries(formatEntries(items));
      }
    }
    loadEntries();
  }, [activePill]);

  const filteredCollections = collections.filter((c) =>
    c.label.toLowerCase().includes(query.toLowerCase())
  );

  const chartData = filteredCollections.map((c) => ({
    label: c.label,
    key: c.key,
    value: counts[c.key] || 0,
  }));

  return (
    <Theme theme="g100"> {/* IBM Carbon dark theme */}
      <HeaderBar />
      <Content className="app-content">
        <Grid fullWidth>
          <Column lg={12} md={8} sm={4}>
            <SearchBox query={query} setQuery={setQuery} />

            <div style={{ marginTop: "1rem", marginBottom: "2rem" }}>
              <PillRow
                pills={filteredCollections}
                activePill={activePill}
                setActivePill={setActivePill}
              />
            </div>

            {activePill && (
              <CollectionSection
                title={
                  collections.find((c) => c.key === activePill)?.label ||
                  "Collection"
                }
                entries={entries}
              />
            )}

            <div style={{ marginTop: "2rem" }}>
              <EntriesChart data={chartData} onBarClick={setActivePill} />
            </div>
          </Column>
        </Grid>
      </Content>
    </Theme>
  );
}

export default App;