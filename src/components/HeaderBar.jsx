// src/components/HeaderBar.jsx
import React, { useEffect, useState } from "react";
import {
  Header,
  HeaderName,
  HeaderGlobalBar,
  HeaderGlobalAction,
  HeaderMenuButton,
  HeaderNavigation,
  HeaderMenuItem,
  SideNav,
  SideNavItems,
} from "@carbon/react";
import { Moon, Sun } from "@carbon/icons-react";
import { Link, useLocation, useNavigate } from "react-router-dom";

/** Carbon md breakpoint ≈ 672px */
const MOBILE_MAX = 672;

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(
    typeof window !== "undefined" ? window.innerWidth < MOBILE_MAX : true
  );
  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth < MOBILE_MAX);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  return isMobile;
}

/** Router-aware Carbon header menu item (prevents full reloads) */
function NavItem({ to, isCurrent, children }) {
  const navigate = useNavigate();
  return (
    <HeaderMenuItem
      href={to}
      isActive={isCurrent}
      onClick={(e) => {
        e.preventDefault();
        navigate(to);
      }}
    >
      {children}
    </HeaderMenuItem>
  );
}

export default function HeaderBar({ theme, toggleTheme }) {
  const isDark = theme === "g90";
  const isMobile = useIsMobile();
  const [isNavOpen, setIsNavOpen] = useState(false);
  const { pathname } = useLocation();
  const navigate = useNavigate();

  const goHome = (e) => {
    e.preventDefault();
    setIsNavOpen(false);
    if (pathname !== "/") navigate("/");
  };

  return (
    <>
      <Header aria-label="Reference Library">
        {/* Mobile-only hamburger */}
        {isMobile && (
          <HeaderMenuButton
            aria-label="Open menu"
            isActive={isNavOpen}
            onClick={() => setIsNavOpen((v) => !v)}
            data-header-action="true"
          />
        )}

        {/* Clickable title -> Home (SPA) */}
        <HeaderName href="/" prefix="" onClick={goHome}>
          Graham Newman reference library
        </HeaderName>

        {/* Desktop nav (hidden on mobile) */}
        {!isMobile && (
          <HeaderNavigation aria-label="Primary navigation">
            <NavItem to="/" isCurrent={pathname === "/"}>Home</NavItem>
            <NavItem
              to="/visualisation"
              isCurrent={pathname.startsWith("/visualisation")}
            >
              Data visualisation
            </NavItem>
          </HeaderNavigation>
        )}

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

      {/* Mobile SideNav */}
      {isMobile && (
        <SideNav
          aria-label="Mobile navigation"
          expanded={isNavOpen}
          onOverlayClick={() => setIsNavOpen(false)}
        >
          <SideNavItems>
            <Link
              to="/"
              className={`cds--side-nav__link${
                pathname === "/" ? " cds--side-nav__link--current" : ""
              }`}
              onClick={() => setIsNavOpen(false)}
              style={{ textDecoration: "none" }}
            >
              <span className="cds--side-nav__link-text">Home</span>
            </Link>

            <Link
              to="/visualisation"
              className={`cds--side-nav__link${
                pathname.startsWith("/visualisation")
                  ? " cds--side-nav__link--current"
                  : ""
              }`}
              onClick={() => setIsNavOpen(false)}
              style={{ textDecoration: "none" }}
            >
              <span className="cds--side-nav__link-text">Data visualisation</span>
            </Link>
          </SideNavItems>
        </SideNav>
      )}
    </>
  );
}