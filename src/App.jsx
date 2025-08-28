import React, { useEffect, useState } from "react";
import { Content, Grid, Column, Button } from "@carbon/react";
import HeaderBar from "./components/HeaderBar";
import PillRow from "./components/PillRow";
import SearchBox from "./components/SearchBox";
import EntriesChart from "./components/EntriesChart";
import CollectionSection from "./components/CollectionSection";
import { fetchCollections, fetchItems, buildCollectionPaths } from "./api";

function App({ toggleTheme, theme }) {
  const [collections, setCollections] = useState([]);
  const [activePill, setActivePill] = useState(null);
  const [entries, setEntries] = useState([]);
  const [query, setQuery] = useState("");
  const [counts, setCounts] = useState({});
  const [paths, setPaths] = useState({});

  useEffect(() => {
    async function loadData() {
      try {
        const colls = await fetchCollections();
        const collsData = colls.map((c) => c.data);
        const children = collsData.filter((c) => c.parentCollection);

        const builtPaths = buildCollectionPaths(collsData);
        setPaths(builtPaths);

        setCollections(
          children.map((c) => ({
            key: c.key,
            label: builtPaths[c.key],
          }))
        );

        const countMap = {};
        for (let c of children) {
          const items = await fetchItems(c.key);
          const clean = items.filter((it) => {
            const t = it.data.title?.trim();
            return t && !["PDF", "UNTITLED"].includes(t.toUpperCase());
          });
          countMap[c.key] = clean.length;
        }
        setCounts(countMap);
      } catch (err) {
        console.error("Error loading data", err);
      }
    }
    loadData();
  }, []);

  useEffect(() => {
    async function loadEntries() {
      if (activePill) {
        const items = await fetchItems(activePill);
        const formatted = items
          .map((it) => {
            const d = it.data;
            const title = d.title?.trim();
            if (!title || ["PDF", "UNTITLED"].includes(title.toUpperCase())) {
              return null;
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
        setEntries(formatted);
      }
    }
    loadEntries();
  }, [activePill]);

  const filteredCollections = collections.filter((c) =>
    c.label.toLowerCase().includes(query.toLowerCase())
  );

  const chartData = collections.map((c) => ({
    label: c.label,
    key: c.key,
    value: counts[c.key] || 0,
  }));

  return (
    <>
      <HeaderBar />
      <Content>
        <Grid className="cds--grid cds--grid--narrow"> {/* Center like Carbon docs */}
          <Column lg={12} md={8} sm={4}>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <Button size="sm" kind="ghost" onClick={toggleTheme}>
                Toggle theme ({theme})
              </Button>
            </div>
            <SearchBox query={query} setQuery={setQuery} />
            <PillRow
              pills={filteredCollections}
              activePill={activePill}
              setActivePill={setActivePill}
            />
            {activePill && (
              <CollectionSection
                title={paths[activePill] || "Collection"}
                entries={entries}
              />
            )}
            <EntriesChart data={chartData} onBarClick={setActivePill} />
          </Column>
        </Grid>
      </Content>
    </>
  );
}

export default App;