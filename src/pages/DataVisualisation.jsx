// src/pages/DataVisualisation.jsx
import React, { useMemo } from "react";
import { useOutletContext, useNavigate, useSearchParams } from "react-router-dom";
import EntriesChart from "../components/EntriesChart.jsx";
import { byYear, byAuthor, toSeries } from "../analytics.js";

export default function DataVisualisation() {
  const { collections, counts, allEntries } = useOutletContext();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const q = searchParams.get("q") || "";

  // 1) Collections (existing)
  const collectionsData = useMemo(
    () =>
      collections.map((c) => ({
        label: c.label,
        key: c.key,
        value: counts[c.key] || 0,
      })),
    [collections, counts]
  );

  // Flatten all entries for analytics
  const flat = useMemo(() => {
    const out = [];
    for (const key of Object.keys(allEntries)) {
      for (const e of allEntries[key] || []) out.push(e);
    }
    return out;
  }, [allEntries]);

  // 2) Timeline (entries per year) — numeric years first, “Unknown” last
  const timelineData = useMemo(() => {
    const series = toSeries(byYear(flat));
    const numeric = series.filter((d) => /^\d{4}$/.test(String(d.label)));
    const unknown = series.filter((d) => !/^\d{4}$/.test(String(d.label)));
    numeric.sort((a, b) => Number(a.label) - Number(b.label));
    return [...numeric, ...unknown];
  }, [flat]);

  // 3) Top Authors — take top 20
  const authorsData = useMemo(() => {
    const series = toSeries(byAuthor(flat));
    series.sort((a, b) => b.value - a.value);
    return series.slice(0, 20);
  }, [flat]);

  const onCollectionClick = (key) => {
    navigate(`/collection/${key}${q ? `?q=${encodeURIComponent(q)}` : ""}`);
  };

  const onYearClick = (year) => {
    navigate(`/${year ? `?q=${encodeURIComponent(year)}` : ""}`);
  };

  const onAuthorClick = (author) => {
    navigate(`/${author ? `?q=${encodeURIComponent(author)}` : ""}`);
  };

  return (
    <>
      <h1 className="section-title" style={{ marginTop: 0 }}>Data visualisation</h1>

      <section>
        <h2 className="section-title">Entries by collection</h2>
        <EntriesChart data={collectionsData} onBarClick={onCollectionClick} />
      </section>

      <section>
        <h2 className="section-title">Timeline (entries per year)</h2>
        {/* Wider scroll surface for many years */}
        <div className="chart-scroll">
          <div style={{ minWidth: 720 }}>
            <EntriesChart data={timelineData} onBarClick={(label) => onYearClick(label)} />
          </div>
        </div>
      </section>

      <section>
        <h2 className="section-title">Top authors</h2>
        {/* Authors can be long — allow horizontal scroll */}
        <div className="chart-scroll">
          <div style={{ minWidth: 900 }}>
            <EntriesChart data={authorsData} onBarClick={(label) => onAuthorClick(label)} />
          </div>
        </div>
      </section>
    </>
  );
}