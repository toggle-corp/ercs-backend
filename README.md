# ERCS-EOC Backend

Backend for the **Ethiopian Red Cross Society (ERCS) Emergency Operations Center (EOC)**. It provides a Strawberry GraphQL API (async ASGI) consumed by the React frontend.

## Tech Stack

- **Python 3.12** / **Django 5.1**
- **PostgreSQL 17**
- **Strawberry GraphQL** (`strawberry-graphql-django ~0.70.1`)
- **Docker Compose** for local development

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/)

---

## Setup

### 1. Configure environment variables

Copy the example env file and update the values:

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```env
DJANGO_SECRET_KEY=your-secret-key-here

# Must be "db" when running inside Docker Compose
POSTGRES_HOST=db
```

The following variables are required and have defaults set in `docker-compose.yml` for local dev — override them in `.env` if needed:

| Variable | Default (dev) | Notes |
|---|---|---|
| `APP_TYPE` | `WEB` | Must be `WEB` |
| `APP_ENVIRONMENT` | `DEV` | |
| `APP_DOMAIN` | `http://localhost:8000` | |
| `FRONTEND_DOMAIN` | `http://localhost:3000` | |
| `SESSION_COOKIE_DOMAIN` | `localhost` | |
| `CSRF_COOKIE_DOMAIN` | `localhost` | |

### 2. Start services

```bash
docker compose up
```

This starts the web server on `http://localhost:8000` and a PostgreSQL database.

### 3. Run migrations

```bash
docker compose run --rm web ./manage.py migrate
```

---

## Creating a Superuser

```bash
docker compose run --rm web ./manage.py createsuperuser
```

You will be prompted for an email, full name, and password. The superuser will have the `SUPERADMIN` role and full access to the Django admin at `http://localhost:8000/admin/`.

---

## Loading Seed Data

The `seed_data/db.json` fixture contains an initial admin user and a set of external dashboards (Power BI embeds) for the Capacity & Resources section.

```bash
docker compose run --rm web ./manage.py loaddata seed_data/db.json
```

> **Note:** The fixture includes a pre-created admin account (`admin@togglecorp.com`). If you have already created a superuser with the same email, the load will fail due to a conflict — either delete the existing user first or skip loading the user fixture.

---

## GraphQL API

The GraphQL endpoint is available at:

```
http://localhost:8000/graphql/
```

### Export the schema

```bash
docker compose run --rm web ./manage.py graphql_schema --out schema.graphql
```

---

## Running Tests

```bash
docker compose run --rm web bash misc/run_tests.sh
```

This runs pytest with coverage. Test files live in `apps/<app>/tests/`.

---

## Linting

Pre-commit hooks are configured with `ruff` for linting and formatting.

```bash
uv run pre-commit run --all-files
```

---

## Apps

| App | Purpose |
|---|---|
| `users` | Custom user model, authentication, roles (Viewer / Staff / Superadmin) |
| `reports` | Reports, manuals, policies, guidelines, links, AI document extraction |
| `dashboards` | External dashboards (Power BI embeds), capacity & resource groups |
| `geo` | Geographic areas (regions, woredas) |
| `teams` | Teams and team members |
| `emergency` | Emergency events |
| `gallery` | Media gallery |
| `content` | CMS-style content |
| `common` | Shared utilities |
