// src/components/HeaderBar.jsx
import React from "react";
import {
  Header,
  HeaderName,
  HeaderNavigation,
  HeaderMenuItem,
  HeaderGlobalBar,
  HeaderGlobalAction,
} from "@carbon/react";
import { Moon, Sun } from "@carbon/icons-react";
import { NavLink } from "react-router-dom";

export default function HeaderBar({ theme, toggleTheme }) {
  const isDark = theme === "g90";

  return (
    <Header aria-label="Reference Library">
      <HeaderName prefix="">Graham Newman reference library</HeaderName>

      {/* Let Carbon own the classes; use NavLink as the element */}
      <HeaderNavigation aria-label="Primary navigation">
        <HeaderMenuItem as={NavLink} to="/" end>
          Home
        </HeaderMenuItem>
        <HeaderMenuItem as={NavLink} to="/visualisation">
          Data visualisation
        </HeaderMenuItem>
      </HeaderNavigation>

      <HeaderGlobalBar>
        <HeaderGlobalAction
          aria-label="Toggle theme"
          onClick={toggleTheme}
          tooltipAlignment="end"
        >
          {isDark ? <Sun size={20} /> : <Moon size={20} />}
        </HeaderGlobalAction>
      </HeaderGlobalBar>
    </Header>
  );
}