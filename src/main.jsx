// src/main.jsx
import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Theme } from "@carbon/react";

import App from "./App.jsx";
import Home from "./pages/Home.jsx";
import DataVisualisation from "./pages/DataVisualisation.jsx";
import CollectionPage from "./pages/Collection.jsx";

import "./index.scss";
import "@carbon/styles/css/styles.css";

function Root() {
  const [theme, setTheme] = useState("g90");
  const toggleTheme = () => setTheme((prev) => (prev === "g90" ? "g10" : "g90"));
  const basename = import.meta.env.BASE_URL || "/";

  return (
    <BrowserRouter basename={basename}>
      <Theme theme={theme}>
        <Routes>
          <Route path="/" element={<App toggleTheme={toggleTheme} theme={theme} />}>
            <Route index element={<Home />} />
            <Route path="visualisation" element={<DataVisualisation />} />
            <Route path="collection/:key" element={<CollectionPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Theme>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);