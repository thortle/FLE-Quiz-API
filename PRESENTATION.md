# FLE Grammar Quiz API - Oral Presentation

ALAO Project - M2 IDL

---

## SLIDE 1: Project Overview (Intro)

**Objective:** Build a FastAPI-based quiz application for French grammar learning (FLE).

**Deliverables:**
- Question database (CSV) – 120+ questions
- FastAPI application with improved documentation
- Request test suite
- Development log

**Tech Stack:**
- Python 3 + FastAPI
- Pandas for CSV handling
- Pydantic for validation
- Uvicorn ASGI server

**Project Structure:**
```
Projet_ALAO_Quiz/
├── main.py           # FastAPI application
├── quiz_terminal.py  # Interactive terminal UI
├── questions.csv     # Question database
├── requests.sh       # Test scripts (16+ tests)
├── requirements.txt  # Dependencies
├── log.txt           # Development log
└── README.md         # Documentation
```

---

## SLIDE 2: Database (Questions CSV)

**Pedagogical Source:**
- Based on *Grammaire Progressive du Francais* (add edition/author details).
- Exercises adapted into multiple-choice questions with one correct answer.

**Format & Fields (CSV, `;`-separated):**
| Field      | Description                                   |
|-----------|-----------------------------------------------|
| question  | Question text with blank (`___`)              |
| categorie | Grammar category                              |
| niveau    | CEFR level (A1–C2)                            |
| reponse   | Correct answer                                |
| reponseA-D| Multiple-choice options                       |
| commentaire | Optional explanation / feedback            |

**Total Questions:** 120+

**Distribution by Level:**
| Level | Count | Description        |
|-------|-------|--------------------|
| A1    | 15    | Beginner           |
| A2    | 20    | Elementary         |
| B1    | 25    | Intermediate       |
| B2    | 25    | Upper Intermediate |
| C1    | 20    | Advanced           |
| C2    | 15    | Proficiency        |

**Distribution by Category:**
| Category   | Count |
|------------|-------|
| verbe      | 62    |
| pronom     | 15    |
| adverbe    | 13    |
| conjonction| 10    |
| adjectif   | 8     |
| preposition| 6     |
| nom        | 5     |
| article    | 1     |

---

## SLIDE 3: Improving the API Documentation

**Goal:** Make the API self-explanatory for teachers and developers using only `/docs` and `README.md`.

### 1. FastAPI Metadata & Global Description

- Principle: **Immediate context** — users should understand the API in one glance.
- Example:
```python
api = FastAPI(
    title="API Quiz FLE - Grammaire Francaise",
    description="API pour un quiz de grammaire francaise...",
    version="1.0.0"
)
```

### 2. Endpoint-Level Documentation (Docstrings & Tags)

- Principle: Each endpoint answers 3 questions:
  - What does it do?
  - What does it expect?
  - What does it return / when does it fail?
- Example:
```python
@api.post("/generate_quiz")
def generate_quiz(request: QuizRequest):
    """Genere un quiz de 10 questions aleatoires selon le niveau."""
```
- Visible effect in Swagger:
  - Clear French descriptions per route
  - Grouping by tags (Info, Quiz, etc.) for easier navigation

### 3. Pydantic Models with Constraints & Examples

- Principle: Documentation and validation in one place.
- Example field constraints:
```python
question: str = Field(min_length=5, max_length=500)
categorie: str = Field(min_length=2, max_length=50)
niveau: str = Field(min_length=2, max_length=2)  # A1, B2, etc.
```
- Benefits:
  - Auto-generated schemas in `/docs`
  - Automatic 422 errors with clear messages when data is invalid

### 4. Clear, User-Oriented Error Messages

- Principle: Explain what went wrong and how to fix it.
- Example:
```python
HTTPException(
    status_code=400,
    detail="Niveau invalide: 'X'. Utilisez A, B, ou C."
)
```
- Talking point: Difference between **technical errors** (422 validation) and **business rules** (400 custom messages).

---

## SLIDE 4: API Performance Evaluation

**Objective:** Verify that the API is fast and behaves correctly under load.

### 1. Techniques & Tools Used

- **Single-request timing:** `curl` with timing options
```bash
curl -w "%{time_total}s\n" http://127.0.0.1:8000/stats
```
- **Concurrent load testing (shell parallelism):**
```bash
time (for i in {1..500}; do 
    curl -s -o /dev/null http://127.0.0.1:8000/stats & 
done; wait)
```

### 2. Results – Individual Endpoints

| Endpoint | Avg Response Time |
|----------|-------------------|
| GET `/`  | ~1.4 ms           |
| GET `/verify` | ~1.4 ms      |
| GET `/stats` | ~2.1 ms       |
| POST `/generate_quiz` | ~1.7 ms |

### 3. Results – Concurrent Requests

| Parallel Requests | Total Time | Avg per Request |
|-------------------|------------|-----------------|
| 50                | ~100 ms    | ~2 ms           |
| 200               | ~600 ms    | ~3 ms           |
| 500               | ~1.3 s     | ~2.6 ms         |

**Key observations (talking points):**
- All endpoints respond in < 2.5 ms (target: < 5 ms).
- API scales approximately linearly: more requests → proportionally more time.
- No request failures under load (0% error rate).
- Limiting factor appears to be shell process spawning, not FastAPI itself.

### 4. Sync vs Async Discussion

- Current implementation: **synchronous endpoints**, executed in FastAPI’s thread pool.
- For this project:
  - Small CSV file, no external services → sync is sufficient.
- For future / higher load:
  - Async endpoints + async database drivers would help for:
    - Real databases (PostgreSQL, Redis)
    - External APIs
    - Thousands of concurrent users

---

## SLIDE 5: Security Measures

**Goal:** Make the API reasonably safe to expose to a frontend and robust against bad inputs.

### 1. CORS Configuration

- Problem: Browsers block cross-origin requests from a separate frontend.
- Solution: Add CORS middleware in FastAPI.
```python
from fastapi.middleware.cors import CORSMiddleware

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # all origins for now (dev)
    allow_methods=["GET", "POST"],
    allow_credentials=True,
    allow_headers=["*"],
)
```
- Verification:
```bash
curl -I -X OPTIONS http://127.0.0.1:8000/stats \
  -H "Origin: http://example.com" \
  -H "Access-Control-Request-Method: GET"
# Response includes: Access-Control-Allow-Origin: *
```

### 2. Input Validation with Pydantic

- Purpose: Block malformed or suspicious input before it reaches our logic.
```python
class QuestionRequest(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    categorie: str = Field(min_length=2, max_length=50)
    niveau: str = Field(min_length=2, max_length=2)  # Forces A1, B2, etc.
    reponse: str = Field(min_length=1, max_length=200)
```
- Effect: Too-short or missing fields → automatic 422 error with details.

### 3. Business Logic Validation

- Purpose: Ensure data is pedagogically valid, not just well-formed.
```python
if request.niveau.upper() not in ["A1", "A2", "B1", "B2", "C1", "C2"]:
    raise HTTPException(status_code=400, detail="Niveau invalide...")

if request.reponse not in [request.reponseA, request.reponseB,
                           request.reponseC, request.reponseD]:
    raise HTTPException(status_code=400,
                        detail="La reponse doit correspondre a une des propositions.")
```

### 4. Production Recommendations (Awareness)

| Current Situation         | Recommended for Production           |
|---------------------------|--------------------------------------|
| `allow_origins=["*"]`    | Restrict to specific frontend hosts  |
| No rate limiting          | Add `slowapi` (e.g. `100/min` per IP)|
| No authentication         | Add JWT-based auth / API keys        |
| HTTP only                 | Use HTTPS with reverse proxy         |
| CSV file storage          | Move to SQLite/PostgreSQL            |

---

## SLIDE 6: Live Demo (Swagger UI + CSV)

**Demo 1: Add a Question via Swagger UI**
1. Open http://127.0.0.1:8000/docs
2. Click POST `/create_question`
3. Click "Try it out"
4. Fill in realistic question data (niveau, categorie, options, commentaire)
5. Execute and show the JSON response confirming success

**Demo 2: Verify in the CSV File**
- Open `questions.csv` (editor / spreadsheet / quick Python script).
- Show that the new line has been appended with the same fields.
- Emphasize that new questions immediately become available for future quizzes and stats.

---

## SLIDE 7: Terminal Quiz Demo

- Command:
```bash
python3 quiz_terminal.py
```
- Flow:
1. Select level (A/B/C)
2. Answer 10 questions
3. See final score
- Message: same database and logic reused in a different interface.

---
