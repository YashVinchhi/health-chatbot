Endpoint path mismatch between Rasa actions and backend:
Rasa actions call verbs like:
GET /health/vaccine-schedule (query param age)
GET /health/outbreaks (query param location)
GET /health/symptoms, /health/prevention-tips
Backend exposes:
GET /api/health/vaccines/{age} (path param)
GET /api/health/outbreaks/{location} (path param)
Consequence: Rasa actions will fail to reach the expected backend routes unless one side is changed. The payload/schema expected by actions (JSON shape) also doesn't match what backend currently returns (backend returns a direct list or simple values).
Recommended fix: either update Rasa actions to call the existing backend paths (e.g., BACKEND_URL + /api/health/vaccines with correct params) or add HTTP routes to backend matching Rasa expectations. I can update Rasa actions (lower risk) or add compatibility endpoints to backend.
Mismatched data shapes:
Rasa actions expect backend to return JSON with fields like "vaccines": list of objects with name & description; backend.vaccination.get_schedule returns a simple list of vaccine names (strings).
Actions code iterates expecting vaccine dicts with 'name' and 'description'.
Recommendation: unify response schemas or adapt one side. E.g., backend could return JSON { vaccines: [ {name, description}, ... ] }.
docker-compose and Rasa CLI commands:
docker-compose.yml lines are suspicious for the rasa service command:
command: run -m http://0.0.0.0:5005 --endpoints endpoints.yml
The usual Rasa CLI would be e.g. "rasa run --enable-api --cors '*' --endpoints endpoints.yml" — the current command looks malformed.
rasa-actions service command is set to run actions using ["rasa", "run", "actions", "--actions", "actions"] — that's okay.
Recommendation: fix the rasa command in docker-compose to "rasa run --enable-api --cors '*' --endpoints endpoints.yml" (or as you prefer).
Rasa endpoints.yml tracker_store and docker-compose DB names:
endpoints.yml uses tracker_store url "postgresql://postgres:postgres@postgres:5432/rasa"
docker-compose's db service uses environment POSTGRES_USER, POSTGRES_PASSWORD and POSTGRES_DB values from .env placeholders. Ensure .env sets DB_USER=postgres, DB_PASSWORD=postgres or change endpoints.yml accordingly.
Also check that postgres DB user has created the "rasa" database; currently db POSTGRES_DB is ${DB_NAME} — mismatch unless .env sets DB_NAME=rasa.
Missing infra files/volumes referenced by docker-compose:
docker-compose mounts ./infra/grafana for provisioning, but I did not find infra/grafana in the repo.
Prometheus config scrapes db:5432 directly — PostgreSQL doesn't expose Prometheus metrics by default; you'd normally use postgres_exporter. This will result in no metrics for Postgres endpoint.
Recommendation: add grafana provisioning files or change volumes, and add a postgres exporter for metrics.
README has a merge artifact:
README ends with conflict markers and duplicate lines (======= and >>>>>>>). You may want to clean that.
.venv is present in repo:
I found a .venv folder tracked in the workspace listing. That bloats repo size. Usually a venv is not committed — ensure .gitignore excludes it and remove from repo if present.
Scripts are bash-only:
scripts/*.sh are bash scripts. On Windows (cmd.exe default) they won't run without WSL/Git Bash. That may be intentional for production, but note for local Windows dev.
Some incomplete implementations / placeholders:
backend.services.* are dummy implementations. Routes in health_api call these services, but they return simple lists/dicts without rich metadata referenced by actions.py.
db.Crud methods accept strings for due_date but model uses DateTime — possible runtime issues.
No tests exist (README suggests pytest backend/tests/) — there is no tests folder.