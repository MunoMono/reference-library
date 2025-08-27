#!/usr/bin/env bash
# List child collections (key + name) with item counts

USER_ID="3436801"
API_KEY="Trlijv6r9XeMU6QF1TcI1YaB"
API="https://api.zotero.org/users/$USER_ID"

COLLS_JSON=$(curl -s -H "Zotero-API-Key: $API_KEY" \
  "$API/collections?limit=200")

echo "$COLLS_JSON" | jq -r '
  [ .[] | select(.data.parentCollection != "") ]
  | .[] | "\(.data.key)|\(.data.name)"
' | while IFS="|" read -r KEY NAME; do
  COUNT=$(curl -s -H "Zotero-API-Key: $API_KEY" \
    "$API/collections/$KEY/items?limit=200" \
    | jq '[.[] | select(.data.title and .data.title != "PDF")] | length')
  echo "$NAME — $COUNT"
done