# Airport Snowflake Ops Dashboard

FastAPI + Snowflake backend with a React/Vite frontend. Ingests Aviationstack flight data, normalizes it into dimension/fact tables, and exposes JWT‑protected APIs for CRUD and analytics.

## Stack
- Backend: FastAPI, Snowflake connector, JWT auth
- Frontend: React + Vite
- DB: Snowflake (DIM_AIRPORT, DIM_AIRLINE, FACT_FLIGHT)

## Setup
1. Create `.env` from `.env.example` and fill values.
2. Create tables (required before running locally or with Docker):
```bash
python scripts/create_tables.py
```
3. Seed a demo user:
```bash
python scripts/seed_user.py
```
4. Start everything:
```bash
docker compose up --build
```

Frontend: `http://localhost:3000`  
API docs: `http://localhost:8000/docs`

## Auth
Supports email/password login and Google OAuth (if configured in `.env`).
Email/password login:
```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"change-me"}'
```
Use the JWT as:
```
Authorization: Bearer YOUR_TOKEN
```

Google OAuth:
- `GET /auth/google/url` returns the Google auth URL
- `GET /auth/google/callback` exchanges code and redirects back with `#token=...` (if `FRONTEND_REDIRECT_URL` is set)

## Core Endpoints
Ingest flights:
```bash
curl -s -X POST 'http://localhost:8000/ingest/flights?dep_iata=ORD&limit=50' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

Unique airlines for an airport:
```bash
curl -s 'http://localhost:8000/airports/ORD/unique-airlines' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

CRUD example (airports):
```bash
curl -s -X POST http://localhost:8000/airports \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"airport_iata":"ORD","airport_name":"O''Hare","timezone":"America/Chicago","icao":"KORD"}'
```

## Tests & Lint
```bash
pytest -q
```
```bash
pip install -r requirements-dev.txt
ruff check .
ruff format
```

## Notes
- All endpoints (except auth) require a JWT.
- Snowflake role/warehouse/database/schema must exist.
