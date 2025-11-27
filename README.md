# FLE Grammar Quiz API

FastAPI application for French grammar quizzes targeting FLE (French as a Foreign Language) learners.

**Source:** Questions based on *Grammaire Progressive du Français* (Intermédiaire)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python3 -m uvicorn main:api --host 127.0.0.1 --port 8000
```

- **API:** http://127.0.0.1:8000
- **Interactive Docs:** http://127.0.0.1:8000/docs (Swagger UI)
- **Terminal Quiz:** `python3 quiz_terminal.py` (requires running server)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and available endpoints |
| GET | `/verify` | Health check + question count |
| GET | `/stats` | Statistics by level and category |
| POST | `/generate_quiz` | Generate 10 random questions by level |
| POST | `/create_question` | Add a new question to database |

### Generate Quiz

```bash
curl -X POST http://127.0.0.1:8000/generate_quiz \
  -H "Content-Type: application/json" \
  -d '{"niveau": "B"}'
```

| Level | CEFR | Description |
|-------|------|-------------|
| A | A1, A2 | Beginner |
| B | B1, B2 | Intermediate |
| C | C1, C2 | Advanced |

**Response:**
```json
{
  "quiz": [...],
  "niveau": "B",
  "nombre_questions": 10
}
```

### Create Question

```bash
curl -X POST http://127.0.0.1:8000/create_question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Elle ___ au marche hier.",
    "categorie": "verbe",
    "niveau": "A2",
    "reponse": "est allee",
    "reponseA": "a alle",
    "reponseB": "est allee",
    "reponseC": "est alle",
    "reponseD": "a allee"
  }'
```

| Field | Required | Description |
|-------|----------|-------------|
| question | Yes | The question text (5-500 chars) |
| categorie | Yes | Grammar category (2-50 chars) |
| niveau | Yes | CEFR level: A1, A2, B1, B2, C1, C2 |
| reponse | Yes | Correct answer (must match an option) |
| reponseA, reponseB | Yes | Answer options (1-200 chars each) |
| reponseC, reponseD | No | Additional options |
| commentaire | No | Explanation |

### Error Handling

| Code | Cause |
|------|-------|
| 400 | Invalid level or answer doesn't match options |
| 404 | No questions found for requested level |
| 422 | Validation error (missing/invalid fields) |

---

## Project Structure

```
├── main.py              # FastAPI application
├── quiz_terminal.py     # Interactive terminal interface
├── questions.csv        # Question database (125+ questions)
├── requests.sh          # Test scripts (16 tests)
├── log.txt              # Development log
└── README.md
```

## Database

| Property | Value |
|----------|-------|
| Format | CSV (semicolon delimiter) |
| Questions | 125+ |
| Levels | A1 (15), A2 (20), B1 (25), B2 (25), C1 (20), C2 (15) |
| Categories | verbe, pronom, adverbe, conjonction, adjectif, preposition, nom, article |

---

## Performance

| Endpoint | Avg Response |
|----------|--------------|
| GET / | 1.4 ms |
| GET /verify | 1.4 ms |
| GET /stats | 2.1 ms |
| POST /generate_quiz | 1.7 ms |

**Load test:** 50 concurrent requests completed in < 100 ms.

## Security

| Feature | Implementation |
|---------|----------------|
| CORS | Enabled (configure specific origins in production) |
| Input Validation | Field length limits, level validation, answer matching |
| Recommendations | Use HTTPS, add rate limiting (slowapi), restrict CORS |

---

## Future Improvements

| Area | Planned Features |
|------|------------------|
| Database | SQLite/PostgreSQL migration, Redis caching, indexing |
| Features | JWT authentication, user scores, DELETE/PUT endpoints, category filtering |
| Interface | Web frontend (React/Vue), mobile app, offline mode |
| DevOps | Docker, pytest, CI/CD (GitHub Actions), monitoring |

---

## Testing

Run all tests:
```bash
chmod +x requests.sh
./requests.sh
```

Tests cover: all endpoints, error cases (400, 404, 422), edge cases, CORS.

---

## License

MIT
