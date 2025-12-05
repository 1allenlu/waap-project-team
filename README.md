# Geographic API (Flask + Flask-RESTX)

Minimal REST API for countries, states, and cities with MongoDB backend and in-memory caching.

## Quick Start
- Python 3.11+, MongoDB running locally (`mongodb://localhost:27017` by default).
- Install dev deps: `make dev_env` (creates/uses your venv if activated).
- Run server (example): `python -m flask --app server.endpoints run --port 5000`
- Run all tests: `make all_tests` (requires Mongo up).
- Lint (project only): `flake8 --exclude .venv`

## Endpoints (13 total)
- Cities: `/cities/read` GET/POST, `/cities` POST, `/cities/<id>` GET/PUT/DELETE
- States: `/state/read` GET, `/state` POST, `/state/<id>` GET/PUT/DELETE
- Countries: `/countries` GET/POST, `/countries/<id>` GET/PUT/DELETE, `/countries/read` GET
- Utility: `/counts` GET, `/health` GET, `/hello` GET, `/endpoints` GET

## Notes
- Mongo configuration via env vars (`MONGO_URI`, or `CLOUD_MONGO` + `MONGO_HOST`/`MONGO_USER_NM`/`MONGO_PASSWD` for cloud).
- Swagger/RESTX models defined in `server/endpoints.py`.
- Tests mock DB calls where possible; integration paths expect Mongo reachable.

## Common Make Targets
- `make dev_env`   — install dev dependencies
- `make all_tests` — run module and endpoint tests
- `make prod`      — tests then push (if configured)
