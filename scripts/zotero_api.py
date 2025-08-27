# scripts/zotero_api.py
from __future__ import annotations
import os, time, requests
from typing import Dict, List, Tuple

API = "https://api.zotero.org"

def _headers() -> Dict[str, str]:
    key = os.environ.get("ZOTERO_API_KEY", "")
    if not key:
        raise RuntimeError("ZOTERO_API_KEY not set")
    # Version header is harmless+recommended
    return {"Zotero-API-Key": key, "Zotero-API-Version": "3"}

def _lib_base() -> str:
    lib_type = (os.environ.get("ZOTERO_LIBRARY_TYPE") or "user").strip().lower()
    lib_id = (os.environ.get("ZOTERO_LIBRARY_ID") or "").strip()
    if lib_type not in ("user", "groups"):
        raise RuntimeError("ZOTERO_LIBRARY_TYPE must be 'user' or 'groups'")
    if not lib_id:
        raise RuntimeError("ZOTERO_LIBRARY_ID not set (e.g., your user ID 3436801)")
    return f"{API}/{lib_type}s/{lib_id}"

def _follow_next(link_header: str) -> str | None:
    for part in (link_header or "").split(","):
        part = part.strip()
        if 'rel="next"' in part:
            return part[part.find("<")+1:part.find(">")]
    return None

def fetch_collections() -> List[Dict]:
    """Fetch all collections (handles pagination)."""
    url = _lib_base() + "/collections"
    params = {"limit": 100}
    out: List[Dict] = []
    while True:
        r = requests.get(url, params=params, headers=_headers(), timeout=30)
        if r.status_code == 403:
            raise RuntimeError("403 from Zotero API. Check API key scopes and library type/ID.")
        r.raise_for_status()
        out.extend(r.json())
        next_url = _follow_next(r.headers.get("Link", ""))
        if not next_url:
            break
        url, params = next_url, {}
        time.sleep(0.1)
    return out

def build_collection_paths(cols: List[Dict], sep: str=" ▸ ") -> Tuple[List[str], Dict[str, str]]:
    """Return sorted human paths + map: collectionKey -> path."""
    by_key = {c["key"]: c for c in cols}
    cache: Dict[str, str] = {}
    def path_for(k: str) -> str:
        if k in cache: return cache[k]
        c = by_key[k]
        name = c["data"]["name"]
        parent = c["data"].get("parentCollection")
        cache[k] = (path_for(parent) + sep + name) if parent else name
        return cache[k]
    for k in by_key.keys():
        path_for(k)
    paths = sorted(set(cache.values()), key=str.casefold)
    return paths, cache

if __name__ == "__main__":
    cols = fetch_collections()
    paths, _ = build_collection_paths(cols)
    for p in paths: print(p)