# FutureFit AI

AI-driven career alignment: parse a resume → extract skills → compare against a target role → generate a
prerequisite-aware learning roadmap → track progress → feed completed skills back into the next analysis.

**Stack:** React 18 + Vite · Framer Motion · Chart.js · FastAPI · MongoDB (Motor, async) · scikit-learn · optional LLM enrichment.

## Run it

### Docker (everything)
```bash
cp backend/.env.example backend/.env      # set JWT_SECRET (and optionally ADMIN_EMAIL / ADMIN_PASSWORD)
docker compose up --build                 # app on http://localhost:8080, API docs on /api/docs
```

### Local development
```bash
# 1) MongoDB:  docker run -d -p 27017:27017 mongo:7
# 2) Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
uvicorn app.main:app --reload            # seeds skills, roles and courses on first start
python -m pytest tests                   # unit tests for the NLP / gap / roadmap engines
# 3) Frontend
cd frontend && npm install && npm run dev   # http://localhost:5173 (proxies /api to :8000)
```

## Architecture

```
React SPA ──/api──▶ FastAPI (async) ──▶ MongoDB
                      ├─ services/skill_extractor  resume sections, skills + confidence, contact, education, experience years
                      ├─ services/taxonomy         alias regex + TF-IDF char-n-gram similarity (scikit-learn), in-memory
                      ├─ services/gap_analysis     matched / partial / missing, weighted readiness score
                      ├─ services/roadmap          prerequisite DAG (Kahn) → time-boxed phases → course picks
                      └─ services/llm              optional: extra skills + coach note (no-op without API key)
```

**Gap scoring.** Each role requires skills weighted 1–5. A skill is *matched* if the user has it, has an accepted
alternative (Django ⇒ FastAPI), or has a skill that implies it (React ⇒ JavaScript); *partial* (capped at 55 % credit)
if TF-IDF similarity + curated relatedness is high enough; otherwise *missing*. Readiness = weighted coverage.

## Database model (MongoDB)

| Collection | Shape | Key indexes |
|---|---|---|
| `users` | name, email, role (`user`/`admin`), password_hash, **profile** (embedded) | `email` unique |
| `resumes` | user_id, title, extracted `text`, **parsed** {skills[], education, certifications, experience_years, contact} | `(user_id, created_at↓)` |
| `skills` | slug, name, category, hours, aliases, prerequisites, related | `slug` unique, `category` |
| `roles` | slug, title, description, project_idea, **skills[{skill, weight, alt[]}]** (embedded) | `slug` unique, text(title, description) |
| `courses` | title, provider, url, level, hours, free, curated, skill_ids[] | `skill_ids` (multikey), `(level, free)`, text(title, provider) |
| `analyses` | user_id, resume_id, role_slug, readiness_score, matched/partial/missing[], category_breakdown, owned_skills | `(user_id, created_at↓)` |
| `roadmaps` | user_id, analysis_id, **phases[{items[]}]**, progress_pct, totals | `(user_id, created_at↓)`, `analysis_id` |
| `progress_events` | user_id, roadmap_id, item_id, type, hours, created_at | `(user_id, type, created_at↓)`, partial-unique `(roadmap_id, item_id)` for `item_completed` |

*Embed vs reference:* data that is always read/written together and bounded in size is embedded (profile, role skills,
roadmap phases); unbounded or independently queried data (events, resumes, analyses) is a separate collection.
Analyses are immutable snapshots, which is what powers the readiness trend. The raw resume file is **not** stored.

## Performance & scalability notes
- Fully async I/O (Motor); CPU-bound work (bcrypt, PDF/DOCX parsing, NLP) runs in the threadpool.
- The taxonomy and its similarity matrix are built once at startup and cached; only admin edits invalidate it.
- Dashboard = **one** request: independent queries run concurrently with `asyncio.gather`, all index-backed; the
  30-day activity chart is a single aggregation.
- Roadmap item toggles are one atomic `findOneAndUpdate` with array filters (no read-modify-write race).
- Stateless API (JWT access + refresh) ⇒ scale horizontally behind a load balancer; add `--workers N` per core.
- Frontend: route-level code splitting, vendor chunking, React Query caching + optimistic updates, gzip, immutable asset caching.
- **Before large scale:** move the auth rate limiter to Redis, store uploaded files in object storage if you need them,
  add Mongo replica set / Atlas, and shard `progress_events` by `user_id` if it grows very large.

## Security
bcrypt hashing · short-lived access tokens + refresh tokens · RBAC (`/api/admin/*` requires `admin`) · login timing
equalised · per-IP rate limits on auth · upload type/size validation · every query scoped by `user_id` · CORS allow-list.
Tokens are kept in `localStorage` for simplicity; for production consider httpOnly cookies.

## Admin API
Set `ADMIN_EMAIL` + `ADMIN_PASSWORD` in `.env`, sign in, and use `/api/docs` → `PUT /admin/roles/{slug}`,
`PUT /admin/skills/{slug}`, `POST /admin/courses`, `GET /admin/stats`.

## Notes
- Seeded courses are official docs/free courses for common skills; skills without one get a *search link*
  (flagged `curated=false`, hidden by default in the Courses page). Replace/extend them via the admin API.
- Hours per skill are estimates; tune them in the `skills` collection.
