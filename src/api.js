const USER_ID = "3436801";
const API_KEY = "Trlijv6r9XeMU6QF1TcI1YaB";
const API = `https://api.zotero.org/users/${USER_ID}`;

export async function fetchCollections() {
  const resp = await fetch(`${API}/collections?limit=200`, {
    headers: { "Zotero-API-Key": API_KEY },
  });
  if (!resp.ok) throw new Error("Failed to fetch collections");
  return await resp.json();
}

export async function fetchItems(collKey) {
  const resp = await fetch(`${API}/collections/${collKey}/items?limit=200`, {
    headers: { "Zotero-API-Key": API_KEY },
  });
  if (!resp.ok) throw new Error("Failed to fetch items");
  return await resp.json();
}

/**
 * Build a map of collection keys → breadcrumb labels
 */
export function buildCollectionPaths(collsData) {
  const lookup = {};
  collsData.forEach((c) => (lookup[c.key] = c));

  function path(c) {
    let parts = [c.name];
    let parent = c.parentCollection;
    while (parent && lookup[parent]) {
      parts.unshift(lookup[parent].name);
      parent = lookup[parent].parentCollection;
    }
    return parts.join(" → ");
  }

  return Object.fromEntries(collsData.map((c) => [c.key, path(c)]));
}