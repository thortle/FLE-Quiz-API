# FLE Grammar Quiz API

A FastAPI-based quiz application for French grammar learning, targeting FLE (Français Langue Étrangère) learners.

**ALAO Project - M2 IDL**

## Features

- **120 grammar questions** across 6 CEFR levels (A1-C2)
- **8 grammar categories**: verbe, pronom, adverbe, conjonction, adjectif, preposition, nom, article
- **Fast API** with < 2.5 ms response times
- **Interactive documentation** via Swagger UI
- **Terminal quiz interface** for standalone practice

**Source:** Questions based on *Grammaire Progressive du Français* (Éditions CLE International)

### About the Source Material

The *Grammaire Progressive du Français* series is a reference work in FLE teaching, published by **Éditions CLE International**, a publisher specializing in French as a Foreign Language resources.

The series consists of 4 volumes:

| Volume | CEFR Levels |
|--------|-------------|
| Débutant | A1–A2 |
| Intermédiaire | B1–B2 |
| Avancé | B2–C1 |
| Perfectionnement | C1–C2 |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python3 -m uvicorn main:api --host 127.0.0.1 --port 8000
```

| Interface | URL / Command |
|-----------|---------------|
| API | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| Terminal Quiz | `python3 quiz_terminal.py` |

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
    "question": "Elle ___ au marché hier.",
    "categorie": "verbe",
    "niveau": "A2",
    "reponse": "est allée",
    "reponseA": "a allé",
    "reponseB": "est allée",
    "reponseC": "est allé",
    "reponseD": "a allée"
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
FLE-Quiz-API/
├── main.py              # FastAPI application
├── quiz_terminal.py     # Interactive terminal quiz
├── questions.csv        # Question database
├── requests.sh          # Test suite
├── requirements.txt     # Python dependencies
├── log.txt              # Development journal
└── README.md            # This file
```

---

## Database

**Format:** CSV with semicolon (`;`) delimiter

| Field | Description |
|-------|-------------|
| question | Question text with blank (`___`) |
| categorie | Grammar category |
| niveau | CEFR level (A1-C2) |
| reponse | Correct answer |
| reponseA-D | Multiple choice options |
| commentaire | Optional explanation |

**Distribution by Level:**

| Level | Count | Description |
|-------|-------|-------------|
| A1 | 15 | Beginner |
| A2 | 20 | Elementary |
| B1 | 25 | Intermediate |
| B2 | 25 | Upper Intermediate |
| C1 | 20 | Advanced |
| C2 | 15 | Proficiency |

**Distribution by Category:**

| Category | Count |
|----------|-------|
| verbe | 62 |
| pronom | 15 |
| adverbe | 13 |
| conjonction | 10 |
| adjectif | 8 |
| preposition | 6 |
| nom | 5 |
| article | 1 |

---

## Performance

All endpoints respond in under 2.5 ms (target: < 5 ms).

| Endpoint | Avg Response Time |
|----------|-------------------|
| GET `/` | 1.4 ms |
| GET `/verify` | 1.4 ms |
| GET `/stats` | 2.1 ms |
| POST `/generate_quiz` | 1.7 ms |

**Load Testing:**

| Concurrent Requests | Total Time |
|---------------------|------------|
| 50 | ~100 ms |
| 200 | ~600 ms |
| 500 | ~1.3 sec |

---

## Security

| Feature | Implementation |
|---------|----------------|
| CORS | Enabled via FastAPI middleware |
| Input Validation | Pydantic field constraints (min/max length) |
| Business Logic | Level validation, answer matching |

**Production Recommendations:**
- Restrict CORS to specific frontend domains
- Add rate limiting with `slowapi`
- Use HTTPS
- Migrate to SQLite/PostgreSQL

---

## Testing

Run the test suite:

```bash
chmod +x requests.sh
./requests.sh
```

Tests cover all endpoints, error cases (400, 404, 422), and CORS.

---

## Future Improvements

| Area | Planned Features |
|------|------------------|
| Database | SQLite/PostgreSQL, Redis caching |
| Features | JWT authentication, user scores, category filtering |
| Interface | Web frontend (React/Vue), mobile app |
| DevOps | Docker, pytest, CI/CD, monitoring |

---

## License

MIT
