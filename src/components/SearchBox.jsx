import React from "react";
import { Search } from "@carbon/react";

function SearchBox({ query, setQuery }) {
  return (
    <Search
      labelText="Search"
      placeholder="Type to filter..."
      size="lg"
      value={query}
      onChange={(e) => setQuery(e.target.value)}
    />
  );
}

export default SearchBox;