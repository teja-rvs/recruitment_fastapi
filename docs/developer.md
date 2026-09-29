# Developer and API guide

This guide describes the behavior implemented in the application and tests.

## Technology

- Python 3.14 and uv
- FastAPI with Pydantic
- SQLAlchemy async sessions with PostgreSQL 18
- Alembic migrations
- JWT bearer authentication and role-based permissions
- pytest with a 90% full-suite coverage requirement

## Local setup

Install dependencies and start PostgreSQL:

```bash
uv sync --group dev
docker compose up -d
cp src/recruitment_fastapi/.env.example src/recruitment_fastapi/.env
```

Set these values in `src/recruitment_fastapi/.env`:

```env
DATABASE_URL=postgresql+psycopg://recruitment:password@localhost:5432/recruitment
SECRET_KEY=<secret used to sign JWTs>
SQL_ECHO=false
```

`DATABASE_URL` and `SECRET_KEY` are required. `SQL_ECHO` defaults to `false`.
The application loads this file directly, but Alembic reads `DATABASE_URL` from
the process environment. Load the file before running migrations:

```bash
set -a
source src/recruitment_fastapi/.env
set +a
uv run alembic -c src/recruitment_fastapi/alembic.ini upgrade head
```

Start the development server:

```bash
uv run uvicorn recruitment_fastapi.main:app --reload
```

The API is available at http://127.0.0.1:8000. Swagger UI is at `/docs`, ReDoc
at `/redoc`, and the OpenAPI schema at `/openapi.json`.

## Architecture

```mermaid
flowchart LR
    Client --> Router[FastAPI routers]
    Router --> Dependency[Auth, permissions, service dependencies]
    Dependency --> Service[Business services]
    Service --> Repository[Repositories]
    Repository --> DB[(PostgreSQL)]
    Service --> Task[FastAPI background task]
    Task --> Job[Recruitment jobs]
    Job --> DB
```

- `routers/` defines HTTP operations and route-level authorization.
- `dependencies/` resolves the current user, checks permissions, and wires
  services to repositories.
- `services/` contains business rules and schedules background work.
- `repositories/` contains SQLAlchemy queries and persistence.
- `models/` contains users, roles, permissions, polymorphic candidates, and
  polymorphic recruitment steps.
- `schemas/` contains request and response validation.
- `states/` defines candidate and recruitment-step state machines.
- `jobs/` creates candidate steps and advances the recruitment process using
  independent database sessions.

The app does not create tables at startup. Schema changes are managed only by
Alembic.

## Authentication and authorization

`POST /auth/signup` and `POST /auth/login` return an HS256 JWT bearer token.
Tokens contain `user_id` and expire after six hours. Protected requests use:

```http
Authorization: Bearer <access_token>
```

Missing or invalid credentials return `401`. Permission failures return `403`.
Permissions use the exact `resource:action` string stored in the database.

Protected router permissions:

- Users: `users:access` plus `users:view` or `users:assign_roles`
- Roles: `roles:access` plus `roles:view`, `roles:create`, or
  `roles:assign_permissions`
- Permissions: `permissions:access` plus `permissions:view` or
  `permissions:create`
- Recruitment steps: `recruitment_steps:access` plus
  `recruitment_steps:view`, `recruitment_steps:assign_interviewer`,
  `recruitment_steps:review`, `recruitment_steps:approve`, or
  `recruitment_steps:reject`

Interview completion, review, approval, and rejection additionally require the
current user to be the step's assigned interviewer.

> There is no seed command or first-administrator bootstrap flow. Signup creates
> a user without roles. The protected role and permission APIs therefore cannot
> bootstrap a fresh database by themselves.

## API summary

The OpenAPI page contains complete request and response schemas.

Public operations:

- `GET /` — welcome response
- `POST /auth/signup` — create a user and return a token
- `POST /auth/login` — authenticate and return a token
- `POST /candidates/register` — register and classify a candidate

User and administration operations:

- `GET /users/`
- `GET /users/{id}/roles`
- `POST /users/{id}/assign_roles`
- `GET|POST /admin/roles/`
- `POST /admin/roles/{id}/assign_permissions`
- `GET|POST /admin/permissions/`

Recruitment operations:

- `GET /recruitment_steps/`
- `POST /recruitment_steps/{id}/assign_interviewer`
- `POST /recruitment_steps/{id}/interview_complete`
- `POST /recruitment_steps/{id}/review`
- `POST /recruitment_steps/{id}/approve`
- `POST /recruitment_steps/{id}/reject`

Important response codes are `400` for invalid workflow transitions, `401` for
invalid authentication, `403` for denied access, `404` for missing resources,
`409` for duplicates, and `422` for request validation failures.

## Recruitment behavior

Candidate type is selected from `experience`:

- 0–3 years: `entry_candidate`
- 4–6 years: `mid_candidate`
- 7–100 years: `senior_candidate`

Registration schedules a background task that creates the appropriate steps and
starts phone screening. Approving a step schedules another task that starts the
next stage or marks the candidate as recruited when all steps are approved.
Rejecting a step rejects the candidate and cancels the other unfinished steps.

Interviewer assignment is restricted by role key:

- Phone screening: `recruiter`
- DS/algorithm: `engineer`, `senior_engineer`, or `staff_engineer`
- LLD: `senior_engineer` or `staff_engineer`
- HLD: `staff_engineer`
- Background verification: `hiring_manager`

An interview date must be after the current UTC date. Approval and rejection
require feedback.

## Migrations

Use the Alembic configuration under the application package; the root
`alembic.ini` points to a migration directory that is not present.

```bash
uv run alembic -c src/recruitment_fastapi/alembic.ini upgrade head
uv run alembic -c src/recruitment_fastapi/alembic.ini revision \
  --autogenerate -m "description"
```

Both commands require `DATABASE_URL` in the process environment.

## Tests

Create a separate test database:

```bash
docker compose exec postgres createdb -U recruitment recruitment_test
```

Create `src/recruitment_fastapi/.env.test`:

```env
DATABASE_URL=postgresql+psycopg://recruitment:password@localhost:5432/recruitment_test
```

The test configuration refuses to use the application database. For integration
or full-suite runs, it applies Alembic migrations automatically and truncates
all application tables before and after each router test.

```bash
uv run pytest
uv run pytest -m unit --no-cov
uv run pytest -m integration --no-cov
uv run pytest --cov-report=html
```

The full suite enables coverage and fails below 90%. Partial suites use
`--no-cov` because they do not cover the whole application.

## Current limitations

- No first-administrator, role, or permission bootstrap process
- No app Docker image, deployment configuration, or CI workflow
- Candidate status exists in the database but is not included in the candidate
  registration response
- Model-level prerequisite helpers are not enforced directly; stage progression
  is controlled by the recruitment process service
