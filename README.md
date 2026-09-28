# Recruitment FastAPI

An API for candidate registration and staged recruitment workflows. It provides
JWT authentication, role-based access control, interviewer assignment, interview
reviews, and candidate approval or rejection.

## Documentation

- [Developer and API guide](docs/developer.md) — setup, architecture, endpoints,
  permissions, migrations, and tests
- [Product guide](docs/product.md) — capabilities, users, business rules, and
  recruitment workflows
- Interactive API reference — http://127.0.0.1:8000/docs while the app is running

## Quick start

Requirements: Python 3.14, [uv](https://docs.astral.sh/uv/), and Docker.

```bash
uv sync --group dev
docker compose up -d
cp src/recruitment_fastapi/.env.example src/recruitment_fastapi/.env
```

Edit `.env` so `DATABASE_URL` uses the Compose credentials, and replace the
example `SECRET_KEY` with a private value:

```env
DATABASE_URL=postgresql+psycopg://recruitment:password@localhost:5432/recruitment
```

Load the settings, apply the schema, and start the API:

```bash
set -a
source src/recruitment_fastapi/.env
set +a
uv run alembic -c src/recruitment_fastapi/alembic.ini upgrade head
uv run uvicorn recruitment_fastapi.main:app --reload
```

Open http://127.0.0.1:8000/docs.

> The project does not yet provide a bootstrap process for the first
> administrator, roles, or permissions. Public signup works, but new users have
> no roles and cannot use protected endpoints until authorization data is
> created outside the current API flow.

See the [developer guide](docs/developer.md) for test database setup and commands.
