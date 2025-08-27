#!/usr/bin/env bash
# Fetch items from Archer sub-collections in Zotero

ZOTERO_USER_ID="3436801"
ZOTERO_API_KEY="Trlijv6r9XeMU6QF1TcI1YaB"
API="https://api.zotero.org/users/$ZOTERO_USER_ID"

# 1. Fetch all collections
COLLS_JSON=$(curl -s -H "Zotero-API-Key: $ZOTERO_API_KEY" "$API/collections?limit=200")

# 2. Find the parent "1 Archer" key
ARCHER_KEY=$(echo "$COLLS_JSON" | jq -r '.[] | select(.data.name == "1 Archer") | .data.key')

if [ -z "$ARCHER_KEY" ] || [ "$ARCHER_KEY" == "null" ]; then
  echo "Parent collection '1 Archer' not found"
  exit 1
fi

# 3. Child collections we want
declare -a CHILDREN=("Articles and papers" "Monographs and thesis" "Secondary commentary")

for CHILD in "${CHILDREN[@]}"; do
  echo "=== $CHILD ==="
  KEY=$(echo "$COLLS_JSON" | jq -r \
    --arg CHILD "$CHILD" \
    --arg PARENT "$ARCHER_KEY" \
    '.[] | select(.data.name == $CHILD and .data.parentCollection == $PARENT) | .data.key')

  if [ -z "$KEY" ] || [ "$KEY" == "null" ]; then
    echo "Sub-collection '$CHILD' not found"
    echo
    continue
  fi

  # Fetch up to 100 items from that sub-collection
  ITEMS=$(curl -s -H "Zotero-API-Key: $ZOTERO_API_KEY" \
    "$API/collections/$KEY/items?limit=100")

  echo "$ITEMS" | jq -r '.[].data.title'
  echo
done