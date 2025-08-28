import React from "react";

function CollectionSection({ title, entries }) {
  return (
    <section className="collection-section">
      <h2>{title}</h2>
      <ul className="entry-list">
        {entries.map((entry, idx) => (
          <li key={idx}>{entry}</li>
        ))}
      </ul>
    </section>
  );
}

export default CollectionSection;