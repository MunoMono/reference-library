import React from "react";

function CollectionSection({ title, entries }) {
  return (
    <section style={{ marginTop: "1.5rem" }}>
      <h2 style={{ marginBottom: "0.5rem" }}>{title}</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {entries.map((e, idx) => (
          <li key={idx} style={{ marginBottom: "0.25rem" }}>
            – {e}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default CollectionSection;