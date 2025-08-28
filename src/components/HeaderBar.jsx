import React from "react";
import { Header, HeaderName } from "@carbon/react";

function HeaderBar() {
  return (
    <Header aria-label="Reference Library">
      <HeaderName href="#" prefix="">
        Reference Library
      </HeaderName>
    </Header>
  );
}

export default HeaderBar;