import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.scss";
import "@carbon/styles/css/styles.css";
import { Theme } from "@carbon/react";

function Root() {
  const [theme, setTheme] = useState("g90"); // default dark

  const toggleTheme = () => {
    setTheme((prev) => (prev === "g90" ? "g10" : "g90"));
  };

  return (
    <Theme theme={theme}>
      <App toggleTheme={toggleTheme} theme={theme} />
    </Theme>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);