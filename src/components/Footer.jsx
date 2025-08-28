import React from "react";

function Footer() {
  const lastUpdated = new Date().toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

  return (
    <footer className="app-footer">
      <p>Last updated {lastUpdated}</p>
    </footer>
  );
}

export default Footer;