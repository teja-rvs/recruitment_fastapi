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

Tests use a separate Postgres database and load `DATABASE_URL` from `src/recruitment_fastapi/tests/.env.test` (that file is gitignored).

1. Create the test database (Postgres must already be running via Compose):

```bash
docker compose exec postgres createdb -U recruitment recruitment_test
```

If the database already exists, Postgres will report that and you can ignore it.

2. Create `src/recruitment_fastapi/tests/.env.test`:

```env
DATABASE_URL=postgresql+asyncpg://recruitment:password@localhost:5432/recruitment_test
```

Use the same user and password as Compose. Point the URL at `recruitment_test`, not the app database.

3. Install dependencies, including the `dev` group (`pytest-cov`):

```bash
uv sync
```

## How to run the project

```bash
uv run uvicorn recruitment_fastapi.main:app --reload
```

## How to run tests

```bash
uv run pytest --cov=src/recruitment_fastapi --cov-report=html
```

HTML coverage output is written to `htmlcov/`.
