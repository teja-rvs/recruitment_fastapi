# Project details

A FastAPI service for registering recruitment candidates. Candidates are stored in PostgreSQL and classified by years of experience using SQLAlchemy joined-table-style polymorphism (single table, `type` discriminator).

## Stack

- Python 3.14
- FastAPI
- SQLAlchemy 2 (async sessions)
- PostgreSQL 18
- Alembic
- Pydantic Settings
- pytest
- uv

## Environment

Settings are loaded from files next to the application package:

- `src/recruitment_fastapi/.env` — app settings
- `src/recruitment_fastapi/.env.test` — test database URL

Example:

```env
DATABASE_URL=postgresql+psycopg://recruitment:password@localhost:5432/recruitment
```

The app reads `DATABASE_URL` via `pydantic-settings`. On startup it creates tables with `Base.metadata.create_all`.

## API

Interactive docs: http://127.0.0.1:8000/docs

### `GET /`

Health/welcome payload.

### `POST /candidates/register`

Register a candidate.

**Request body**

| Field        | Rules                                     |
| ------------ | ----------------------------------------- |
| `name`       | string, 3–26 characters                   |
| `email`      | valid email, unique                       |
| `phone`      | valid phone number (e.g. `+919999999999`) |
| `experience` | integer, 0–100                            |

**Example**

```bash
curl -X POST http://127.0.0.1:8000/candidates/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "phone": "+919999999999",
    "experience": 4
  }'
```

**Success (200)** includes `id` and `type`. Duplicate email or phone returns **409**. Invalid input returns **422**.

### Candidate types

`type` is assigned from `experience`:

| Experience | Type              |
| ---------- | ----------------- |
| 0–3 years  | `entry_candidate` |
| 4–6 years  | `mid_candidate`   |
| 7+ years   | `senior_candidate` |

## Migrations

Alembic lives under `src/recruitment_fastapi/alembic`. `env.py` uses `DATABASE_URL` from the environment.

```bash
uv run alembic -c src/recruitment_fastapi/alembic.ini upgrade head
```

Generate a revision:

```bash
uv run alembic -c src/recruitment_fastapi/alembic.ini revision --autogenerate -m "description"
```

## Project layout

```
src/recruitment_fastapi/
  main.py                 # FastAPI app, lifespan, integrity handler
  config.py               # Settings from .env
  database.py             # Async engine and session
  routers/candidates.py   # HTTP layer
  services/candidate.py   # Type selection and create flow
  respositories/          # Persistence
  models/                 # Candidate + entry/mid/senior subclasses
  schemas/candidates.py   # Request/response models
  tests/                  # API tests
  alembic/                # Migrations
docker-compose.yml        # Local Postgres
```
