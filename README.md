# Recruitment FastAPI

Candidate registration API. See [docs/project.md](docs/project.md) for stack, API, and layout.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Docker (for PostgreSQL)

## Setup

```bash
uv sync
docker compose up -d
docker compose exec postgres createdb -U recruitment recruitment_test
```

Copy `src/recruitment_fastapi/.env` if needed. Default Postgres user/db from Compose is `recruitment`.

## How to run the project

```bash
uv run uvicorn recruitment_fastapi.main:app --reload
```

## How to run tests

```bash
uv run pytest --cov=src/recruitment_fastapi --cov-report=html
```
