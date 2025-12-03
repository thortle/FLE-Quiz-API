#!/bin/bash
# =============================================================================
# API Quiz FLE - Test Script
# =============================================================================
# Usage: ./requests.sh
# Requires: API server running on http://127.0.0.1:8000
# Start server: python3 -m uvicorn main:api --host 127.0.0.1 --port 8000
# =============================================================================

BASE_URL="http://127.0.0.1:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=============================================="
echo "API Quiz FLE - Test Suite"
echo "=============================================="
echo ""

# -----------------------------------------------------------------------------
# TEST 1: GET / - API Info
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 1] GET / - API Info${NC}"
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 2: GET /verify - Health Check
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 2] GET /verify - Health Check${NC}"
curl -s "$BASE_URL/verify" | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 3: GET /stats - Statistics
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 3] GET /stats - Statistics${NC}"
curl -s "$BASE_URL/stats" | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 4: POST /generate_quiz - Level A (Débutant)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 4] POST /generate_quiz - Level A${NC}"
curl -s -X POST "$BASE_URL/generate_quiz" \
  -H "Content-Type: application/json" \
  -d '{"niveau": "A"}' | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 5: POST /generate_quiz - Level B (Intermédiaire)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 5] POST /generate_quiz - Level B${NC}"
curl -s -X POST "$BASE_URL/generate_quiz" \
  -H "Content-Type: application/json" \
  -d '{"niveau": "B"}' | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 6: POST /generate_quiz - Level C (Avancé)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 6] POST /generate_quiz - Level C${NC}"
curl -s -X POST "$BASE_URL/generate_quiz" \
  -H "Content-Type: application/json" \
  -d '{"niveau": "C"}' | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 7: POST /generate_quiz - Lowercase niveau
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 7] POST /generate_quiz - Lowercase 'b' (should work)${NC}"
curl -s -X POST "$BASE_URL/generate_quiz" \
  -H "Content-Type: application/json" \
  -d '{"niveau": "b"}' | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 8: POST /generate_quiz - Invalid niveau (error case)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 8] POST /generate_quiz - Invalid niveau 'X' (expect error 400)${NC}"
curl -s -X POST "$BASE_URL/generate_quiz" \
  -H "Content-Type: application/json" \
  -d '{"niveau": "X"}' | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 9: POST /generate_quiz - Empty niveau (error case)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 9] POST /generate_quiz - Empty niveau (expect error 400)${NC}"
curl -s -X POST "$BASE_URL/generate_quiz" \
  -H "Content-Type: application/json" \
  -d '{"niveau": ""}' | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 10: POST /create_question - Valid question (all fields)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 10] POST /create_question - Valid question with all fields${NC}"
curl -s -X POST "$BASE_URL/create_question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Elle ___ au marché hier.",
    "categorie": "verbe",
    "niveau": "A2",
    "reponse": "est allée",
    "reponseA": "a allé",
    "reponseB": "est allée",
    "reponseC": "est allé",
    "reponseD": "a allée",
    "commentaire": "Passé composé avec être pour les verbes de mouvement"
  }' | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 11: POST /create_question - Minimal fields (only required)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 11] POST /create_question - Minimal fields (A/B only)${NC}"
curl -s -X POST "$BASE_URL/create_question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Le chat ___ sur le toit.",
    "categorie": "verbe",
    "niveau": "A1",
    "reponse": "est",
    "reponseA": "est",
    "reponseB": "sont"
  }' | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 12: POST /create_question - Invalid niveau (error case)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 12] POST /create_question - Invalid niveau 'Z1' (expect error 400)${NC}"
curl -s -X POST "$BASE_URL/create_question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Test question",
    "categorie": "verbe",
    "niveau": "Z1",
    "reponse": "oui",
    "reponseA": "oui",
    "reponseB": "non"
  }' | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 13: POST /create_question - Answer mismatch (error case)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 13] POST /create_question - Answer not in options (expect error 400)${NC}"
curl -s -X POST "$BASE_URL/create_question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Test question",
    "categorie": "verbe",
    "niveau": "A1",
    "reponse": "maybe",
    "reponseA": "oui",
    "reponseB": "non"
  }' | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 14: GET /stats - Verify count after additions
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 14] GET /stats - Verify question count after additions${NC}"
curl -s "$BASE_URL/stats" | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 15: Invalid endpoint (404)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 15] GET /invalid - Non-existent endpoint (expect 404)${NC}"
curl -s "$BASE_URL/invalid" | python3 -m json.tool
echo ""

# -----------------------------------------------------------------------------
# TEST 16: Wrong HTTP method (405)
# -----------------------------------------------------------------------------
echo -e "${BLUE}[TEST 16] GET /generate_quiz - Wrong method (expect 405)${NC}"
curl -s "$BASE_URL/generate_quiz" | python3 -m json.tool
echo ""

echo "=============================================="
echo "Test Suite Complete"
echo "=============================================="
