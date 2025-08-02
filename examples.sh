#!/bin/bash

# FIX Dictionary API Examples
# This script demonstrates various API calls

BASE_URL="http://localhost:8000"
# For production, use: BASE_URL="https://your-domain.vercel.app"

echo "=== FIX Dictionary API Examples ==="
echo "Base URL: $BASE_URL"
echo

# Health check
echo "1. Health Check:"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo

# Get available versions
echo "2. Available FIX Versions:"
curl -s "$BASE_URL/api/versions" | python3 -m json.tool
echo

# Search for "Order"
echo "3. Search for 'Order':"
curl -s "$BASE_URL/api/search?query=Order&version=FIX.5.0SP2" | python3 -m json.tool | head -20
echo "... (truncated)"
echo

# Get NewOrderSingle message details
echo "4. Get NewOrderSingle Message (type 'D'):"
curl -s "$BASE_URL/api/messages/D?version=FIX.5.0SP2" | python3 -m json.tool | head -30
echo "... (truncated)"
echo

# Get ClOrdID field details
echo "5. Get ClOrdID Field (tag 11):"
curl -s "$BASE_URL/api/fields/11?version=FIX.5.0SP2" | python3 -m json.tool | head -20
echo "... (truncated)"
echo

# Get Side field enum values
echo "6. Get Side Field Enum Values (tag 54):"
curl -s "$BASE_URL/api/codesets/54?version=FIX.5.0SP2" | python3 -m json.tool
echo

# List all messages
echo "7. List Messages (first 5):"
curl -s "$BASE_URL/api/messages?version=FIX.5.0SP2" | python3 -m json.tool | head -30
echo "... (truncated)"
echo

# Search with regex
echo "8. Regex Search for fields starting with 'Order':"
curl -s "$BASE_URL/api/search?query=^Order&search_type=field&is_regex=true&version=FIX.5.0SP2" | python3 -m json.tool
echo

# Get categories
echo "9. Available Categories:"
curl -s "$BASE_URL/api/categories?version=FIX.5.0SP2" | python3 -m json.tool
echo

echo "=== Examples completed ==="
echo "Visit $BASE_URL/docs for interactive API documentation"
