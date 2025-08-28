// src/api.js
const USER_ID = "3436801";
const API_KEY = "Trlijv6r9XeMU6QF1TcI1YaB";
const API_BASE = `https://api.zotero.org/users/${USER_ID}`;

export async function fetchCollections() {
  const resp = await fetch(`${API_BASE}/collections?limit=200`, {
    headers: { "Zotero-API-Key": API_KEY },
  });
  if (!resp.ok) throw new Error("Failed to fetch collections");
  return resp.json();
}

export async function fetchItems(collKey) {
  const resp = await fetch(`${API_BASE}/collections/${collKey}/items?limit=200`, {
    headers: { "Zotero-API-Key": API_KEY },
  });
  if (!resp.ok) throw new Error("Failed to fetch items");
  return resp.json();
}