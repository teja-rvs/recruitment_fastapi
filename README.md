# Recruitment FastAPI

Candidate registration API. See [docs/project.md](docs/project.md) for stack, API, and layout.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Docker (for PostgreSQL)

## Setup

```bash
uv sync
docker compose up -d
```

Copy `src/recruitment_fastapi/.env.example` to `src/recruitment_fastapi/.env` if needed. Default Compose credentials are user `recruitment`, password `password`, database `recruitment`.

## Test environment

Tests are split by marker:

- `unit` — repository and service tests. No database, no HTTP stack. They run without `.env.test`.
- `integration` — router tests. They use a separate Postgres database and truncate the `candidates` table before and after each test.

Integration tests read `DATABASE_URL` from `src/recruitment_fastapi/.env.test` (gitignored) and refuse to start if that file is missing or points at the same database as `src/recruitment_fastapi/.env`.

1. Create the test database (Postgres must already be running via Compose):

```bash
docker compose exec postgres createdb -U recruitment recruitment_test
```

If the database already exists, Postgres will report that and you can ignore it.

2. Create `src/recruitment_fastapi/.env.test`:

```env
DATABASE_URL=postgresql+psycopg://recruitment:password@localhost:5432/recruitment_test
```

Use the same user and password as Compose. Point the URL at `recruitment_test`, not the app database.

3. Apply migrations to the test database. The suite truncates tables but never creates them:

```bash
DATABASE_URL=postgresql+psycopg://recruitment:password@localhost:5432/recruitment_test \
  uv run alembic -c src/recruitment_fastapi/alembic.ini upgrade head
```

4. Install dependencies, including the `dev` group (`pytest-cov`):

```bash
uv sync
```

## How to run the project

```bash
uv run uvicorn recruitment_fastapi.main:app --reload
```

## How to run tests

Coverage is enabled by default (`--cov --cov-report=term-missing` in `pyproject.toml`) and the suite fails below 90%:

```bash
uv run pytest
```

Unit tests only. Pass `--no-cov`, since a partial run cannot meet the 90% gate:

```bash
uv run pytest -m unit --no-cov
```

Integration tests only (needs the test database from above):

```bash
uv run pytest -m integration
```

For an HTML report:

```bash
uv run pytest --cov-report=html
```

HTML coverage output is written to `htmlcov/`.
