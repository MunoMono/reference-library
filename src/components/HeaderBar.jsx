import React, { useEffect, useState } from "react";
import { Header, HeaderName, HeaderGlobalBar, HeaderGlobalAction } from "@carbon/react";
import { Sun, Moon } from "@carbon/icons-react";

function HeaderBar() {
  const [theme, setTheme] = useState("g90");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  return (
    <Header aria-label="Reference Library">
      <HeaderName href="#" prefix="">
        Reference Library
      </HeaderName>
      <HeaderGlobalBar>
        <HeaderGlobalAction
          aria-label="Toggle theme"
          onClick={() => setTheme(theme === "g90" ? "g10" : "g90")}
        >
          {theme === "g90" ? <Sun size={20} /> : <Moon size={20} />}
        </HeaderGlobalAction>
      </HeaderGlobalBar>
    </Header>
  );
}

export default HeaderBar;