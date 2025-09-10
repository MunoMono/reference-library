// src/pages/Collection.jsx
import React, { useMemo } from "react";
import { useOutletContext, useParams, useSearchParams, Link } from "react-router-dom";
import Crumb from "../components/Crumb.jsx";
import CollectionSection from "../components/CollectionSection.jsx";
import NotesTag from "../components/NotesTag.jsx";

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
function highlightHTML(text, query) {
  if (!query?.trim() || !text) return text;
  const re = new RegExp(`(${escapeRegExp(query.trim())})`, "gi");
  return String(text).replace(re, "<mark>$1</mark>");
}

export default function CollectionPage() {
  const { key } = useParams();
  const [searchParams] = useSearchParams();
  const q = searchParams.get("q") || "";

  const { allEntries, paths } = useOutletContext();
  const label = paths[key] || "Collection";
  const entries = allEntries[key] || [];

  const items = useMemo(() => {
    return entries.map((e) => (
      <span key={e.id}>
        <span dangerouslySetInnerHTML={{ __html: highlightHTML(e.title, q) }} />
        {" — "}
        <span
          dangerouslySetInnerHTML={{
            __html: highlightHTML((e.authors || []).join(", "), q),
          }}
        />
        {e.year ? `, ${e.year}` : ""}{" "}
        {e.venue ? (
          <em>
            {" — "}
            <span dangerouslySetInnerHTML={{ __html: highlightHTML(e.venue, q) }} />
          </em>
        ) : null}
        {" "}
        {e.hasNotes && <NotesTag href={e.notesUrl} />}
      </span>
    ));
  }, [entries, q]);

  return (
    <>
      <Crumb
        trail={[
          { label: "Home", to: "/" },
          { label, isCurrentPage: true },
        ]}
      />

      <h1 className="section-title" style={{ marginTop: 0 }}>{label}</h1>

      <CollectionSection
        title={`${items.length} entr${items.length === 1 ? "y" : "ies"}`}
        entries={items}
      />

      <p style={{ marginTop: "1rem" }}>
        <Link to={q ? `/?q=${encodeURIComponent(q)}` : "/"}>← Back to search</Link>
      </p>
    </>
  );
}