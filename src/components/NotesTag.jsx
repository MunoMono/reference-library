// src/components/NotesTag.jsx
import React from "react";
import { Tag } from "@carbon/react";

/**
 * Carbon Tag that behaves like a link out to your reading note.
 * Opens in a new tab, preserves accessibility, and stays thematically consistent.
 */
export default function NotesTag({ href }) {
  if (!href) return null;

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Open reading note in a new tab"
      style={{ textDecoration: "none" }}
      className="notes-tag-link"
    >
      <Tag type="blue" title="Notes available">
        Notes
      </Tag>
    </a>
  );
}