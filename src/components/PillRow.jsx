import React from "react";
import { Tag } from "@carbon/react";

function PillRow({ pills, activePill, setActivePill }) {
  return (
    <div style={{ margin: "1rem 0", display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
      {pills.map((pill) => (
        <Tag
          key={pill.key}
          type={activePill === pill.key ? "blue" : "cool-gray"}
          size="md"
          onClick={() => setActivePill(pill.key)}
          style={{ cursor: "pointer" }}
        >
          {pill.label}
        </Tag>
      ))}
    </div>
  );
}

export default PillRow;