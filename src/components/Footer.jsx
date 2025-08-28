import React from "react";

function Footer() {
  const today = new Date();
  const formatted = today.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

  return (
    <footer className="app-footer">
      <small>Last updated {formatted}</small>
    </footer>
  );
}

export default Footer;