# FLE Grammar Quiz API - Oral Presentation

ALAO Project - M2 IDL

---

## SLIDE 1: Project Overview

**Objective:** Build a FastAPI-based quiz application for French grammar learning

**Deliverables:**
- Question database (CSV) - 120+ questions
- FastAPI application with documentation
- Test suite
- Development log

**Tech Stack:**
- Python 3 + FastAPI
- Pandas for data handling
- Pydantic for validation
- Uvicorn ASGI server

**Project Structure:**
```
Projet_ALAO_Quiz/
├── main.py           # FastAPI application
├── quiz_terminal.py  # Interactive terminal UI
├── questions.csv     # Question database
├── requests.sh       # Test scripts (16 tests)
├── requirements.txt  # Dependencies
├── log.txt           # Development log
└── README.md         # Documentation
```

---

## SLIDE 2: Database

**Source:** *Grammaire Progressive du Francais* 

**Format:** CSV with semicolon (;) delimiter

**Fields:**
| Field | Description |
|-------|-------------|
| question | The question text with blank (___) |
| categorie | Grammar category |
| niveau | CEFR level (A1-C2) |
| reponse | Correct answer |
| reponseA-D | Multiple choice options |
| commentaire | Optional explanation |

**Total Questions:** 120+

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

## SLIDE 3: API Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and available endpoints |
| GET | `/verify` | Health check + question count |
| GET | `/stats` | Statistics by level and category |
| POST | `/generate_quiz` | Generate 10 random questions |
| POST | `/create_question` | Add a new question |

**Interactive Documentation:** Swagger UI at http://127.0.0.1:8000/docs

**Documentation Improvements Made:**

1. **FastAPI Metadata:**
```python
api = FastAPI(
    title="API Quiz FLE - Grammaire Francaise",
    description="API pour un quiz de grammaire francaise...",
    version="1.0.0"
)
```

2. **Endpoint Docstrings (French):**
```python
@api.post("/generate_quiz")
def generate_quiz(request: QuizRequest):
    """Genere un quiz de 10 questions aleatoires selon le niveau."""
```

3. **Pydantic Field Validation:**
```python
question: str = Field(min_length=5, max_length=500)
categorie: str = Field(min_length=2, max_length=50)
niveau: str = Field(min_length=2, max_length=2)  # A1, B2, etc.
```

4. **Clear Error Messages:**
```python
HTTPException(status_code=400, 
    detail="Niveau invalide: 'X'. Utilisez A, B, ou C.")
```

---

## SLIDE 4: Performance Evaluation

**How We Tested:**

1. **Individual Response Times** - Using `curl` with timing:
```bash
curl -w "%{time_total}s" http://127.0.0.1:8000/stats
```

2. **Concurrent Load Testing** - Parallel requests in bash:
```bash
time (for i in {1..500}; do 
    curl -s -o /dev/null http://127.0.0.1:8000/stats & 
done; wait)
```

**Results - Individual Endpoints:**

| Endpoint | Avg Response Time |
|----------|-------------------|
| GET / | 1.4 ms |
| GET /verify | 1.4 ms |
| GET /stats | 2.1 ms |
| POST /generate_quiz | 1.7 ms |

**Results - Concurrent Load:**

| Parallel Requests | Total Time | Avg per Request |
|-------------------|------------|-----------------|
| 50 | ~100 ms | ~2 ms |
| 200 | 600 ms | ~3 ms |
| 500 | 1.3 sec | ~2.6 ms |

**Observations:**
- All endpoints respond in < 2.5 ms (target was < 5 ms)
- API scales linearly: 10x more requests = ~10x more time
- No request failures under load (0% error rate)
- Response time stays consistent even under stress (~2-3 ms)
- Limiting factor: shell process spawning, not the API itself

**Sync vs Async:**
- Current implementation uses synchronous endpoints
- FastAPI runs sync functions in a thread pool automatically
- Sufficient for our use case: small CSV dataset, simple I/O
- Async would benefit: database connections, external APIs, 1000+ concurrent users

---

## SLIDE 5: Security

**1. CORS (Cross-Origin Resource Sharing) Middleware**

*What is it?* Browser security that blocks web pages from making requests to different domains.

*Problem:* A frontend app at `http://myquiz.com` cannot call our API at `http://127.0.0.1:8000` - the browser blocks it.

*Solution:* We added CORS middleware to allow cross-origin requests:
```python
from fastapi.middleware.cors import CORSMiddleware

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Which domains can access (all for dev)
    allow_methods=["GET", "POST"],  # Allowed HTTP methods
    allow_credentials=True,
    allow_headers=["*"],
)
```

*How we tested it:*
```bash
curl -I -X OPTIONS http://127.0.0.1:8000/stats \
  -H "Origin: http://example.com" \
  -H "Access-Control-Request-Method: GET"
# Response includes: Access-Control-Allow-Origin: *
```

**2. Input Validation (Pydantic)**

*What it prevents:* Malformed data, injection attacks, database overflow

```python
class QuestionRequest(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    categorie: str = Field(min_length=2, max_length=50)
    niveau: str = Field(min_length=2, max_length=2)  # Forces A1, B2, etc.
    reponse: str = Field(min_length=1, max_length=200)
```

*Effect:* Sending `{"question": "Hi"}` (too short) returns 422 error automatically.

**3. Business Logic Validation**

*What it prevents:* Invalid data that passes format checks

```python
if request.niveau.upper() not in ["A1", "A2", "B1", "B2", "C1", "C2"]:
    raise HTTPException(status_code=400, detail="Niveau invalide...")

if request.reponse not in [request.reponseA, request.reponseB, ...]:
    raise HTTPException(status_code=400, detail="La reponse doit correspondre...")
```

**Recommendations for Production:**

| Current Risk | Recommendation |
|--------------|----------------|
| `allow_origins=["*"]` | Restrict to specific frontend domains |
| No rate limiting | Add slowapi: `@limiter.limit("100/minute")` |
| No authentication | Add JWT tokens for user tracking |
| HTTP only | Use HTTPS in production |
| CSV file storage | Migrate to SQLite/PostgreSQL database |
| No frontend | Build web frontend (React/Vue) |

---

## SLIDE 6: Live Demo

**Demo 1: Add a Question via Swagger UI**
1. Open http://127.0.0.1:8000/docs
2. Click POST /create_question
3. Click "Try it out"
4. Fill in question data
5. Execute and verify response

**Demo 2: Terminal Quiz**
```bash
python3 quiz_terminal.py
```
1. Select level (A/B/C)
2. Answer 10 questions
3. See final score

---

## SLIDE 7: AI Usage

**Tool Used:** Claude

**How We Used It:**

1. **Debugging** - Identifying issues in code logic and suggesting fixes
2. **Documentation Organizer** - Structuring README
3. **Identifying Improvements** - Suggesting security measures, performance optimizations, and best practices

---
