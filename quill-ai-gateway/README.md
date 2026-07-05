# QUILL AI Gateway

A small, boring, private Flask service that lets the open-source [QUILL](https://github.com/Community-Access/quill)
desktop client offer free, hosted AI features **without ever embedding a
shared provider API key in the open-source client**.

**Read this first:** [`docs/planning/openai.md`](../docs/planning/openai.md)
at the repository root is the full product requirements document this
service implements — the *why* behind every decision here. This README is
the *how to run it*; the PRD is the *why it works this way*. If something
here seems arbitrary, the PRD almost certainly explains the reasoning.

## The one-sentence version

QUILL's desktop client holds a QUILL-issued token, never an OpenAI key;
this service is the only thing that ever holds the real key, and it
checks a user's quota *before* every OpenAI call, not after.

## Architecture at a glance

```
QUILL desktop client
      │  HTTPS, Bearer <gateway-token>
      ▼
This Flask app  ──────────────────────────►  OpenAI (one nano-class model)
      │
      ├── PostgreSQL   (users, devices, usage history, admin config)
      └── Redis        (rate-limit counters, config cache)
```

- **`app/config.py`** — every environment variable this service reads, and
  nothing else. Read this to see exactly what a deployment must configure.
- **`app/models.py`** — the full data model (matches PRD §5 exactly).
- **`app/auth.py`** — OAuth 2.0 Device Authorization Grant (RFC 8628) sign-in,
  matching QUILL's existing `device_login.py`/`copilot_auth.py` client-side
  pattern, plus the bearer-token verification every route depends on.
- **`app/limits.py`** — the quota engine. **Every number a user can hit a
  limit on lives here**, and every one of those numbers is admin-tunable
  live from `gateway_config` (see below) — nothing is a hardcoded constant
  except the fail-safe defaults used only if the config table is empty.
- **`app/model_registry.py`** — which OpenAI models are turned on, and
  which one is the active default. An admin can add a model, disable one
  that's misbehaving, or switch the default, all without a deploy.
- **`app/prompts.py`** — the fixed, server-side-only system prompt per
  feature. The client only ever supplies a user prompt/question, never a
  system prompt — this is what stops a modified client from smuggling an
  unapproved use through an approved feature.
- **`app/openai_client.py`** — the *only* place this codebase ever talks to
  OpenAI. If you're auditing "does the key ever leak," this is the one
  file to check.
- **`app/routes/`** — the four blueprints: `device` (auth), `chat` (the one
  inference endpoint), `client_config` (read-only config/quota for the
  client's status display), `admin` (everything an operator needs).
- **`app/cli.py`** — operational commands (`init-db`, `seed-config`,
  `cleanup-expired`, `reconcile-usage`) — see "Running scheduled jobs" below.

## Quick start (local development)

```bash
cd quill-ai-gateway
python -m venv .venv
.venv/Scripts/activate        # or: source .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt

cp .env.example .env
# Edit .env: set a real OPENAI_API_KEY and a generated GATEWAY_SECRET_KEY.
# For local dev, DATABASE_URL can point at a local Postgres, or you can
# skip Postgres entirely for a quick look by using SQLite:
#   DATABASE_URL=sqlite:///dev.db
# Redis is required even locally -- run one with Docker if you don't have
# it installed: docker run -p 6379:6379 redis

flask --app run.py init-db
flask --app run.py seed-config
flask --app run.py run              # or: python run.py
```

Register your own device (so you can reach `/admin/*`):

1. `curl -X POST http://localhost:5000/v1/device/code` — note the `user_code`.
2. Visit `http://localhost:5000/connect?code=<user_code>` in a browser,
   click Confirm.
3. `curl -X POST http://localhost:5000/v1/device/token -d '{"device_code": "<device_code>"}' -H 'Content-Type: application/json'`
   — note the `device_id` in the response.
4. Add that `device_id` to `GATEWAY_ADMIN_ALLOWLIST` in `.env`, restart.

## Running the tests

```bash
cd quill-ai-gateway
pip install -r requirements-dev.txt
pytest
```

The suite uses an in-memory SQLite database and `fakeredis` — no external
services required (see `tests/conftest.py`). 34 tests cover the quota
engine, the large-document safeguards, the device-code auth flow, the
model registry, and the admin API.

## Deployment

Recommended: **the same server already running GLOW and `quillin-hub`**
(see PRD §16 for the full reasoning — reusing known-good infrastructure
beats standing up a new platform for a service this size).

```bash
pip install -r requirements.txt
flask --app run.py init-db      # first deploy only
flask --app run.py seed-config  # first deploy only; safe to re-run later
gunicorn -w 2 -b 127.0.0.1:8001 'app:create_app()'
```

Put this behind the same reverse proxy (nginx/Caddy) that already
terminates TLS for `quillin-hub`, proxying `gateway.quillforall.org` (or
whatever subdomain you choose) to `127.0.0.1:8001`.

**Secrets:** set `OPENAI_API_KEY`, `GATEWAY_SECRET_KEY`, `DATABASE_URL`,
and `GATEWAY_ADMIN_ALLOWLIST` through whatever mechanism already injects
secrets for GLOW/`quillin-hub` on this host — an environment file kept
outside any git-tracked directory, or the platform's secret store if it's
a managed one. **Never** commit a filled-in `.env`. See PRD §6 for the
full secret-management plan, including the key-rotation runbook.

### Running scheduled jobs

Add to cron (adjust paths/venv activation for your setup):

```cron
# Daily: delete expired diagnostic records (PRD §4.4 retention).
0 3 * * * cd /path/to/quill-ai-gateway && .venv/bin/flask --app run.py cleanup-expired

# Nightly: reconcile monthly_usage_summary against the durable event log,
# in case a crash ever left the running aggregate slightly behind
# (app/limits.py::record_usage's docstring explains why this is a safety
# net, not a routine necessity).
30 3 * * * cd /path/to/quill-ai-gateway && .venv/bin/flask --app run.py reconcile-usage
```

Partition maintenance for `usage_events` (production/Postgres only) is a
manual monthly task — see `migrations/README.md`.

## Operating the service day to day (the admin API)

Every route below requires `Authorization: Bearer <your-admin-device-token>`,
and your device must be in `GATEWAY_ADMIN_ALLOWLIST`.

| I want to... | Call |
|---|---|
| See every configured model | `GET /admin/models` |
| Turn a model off (e.g. it's misbehaving) | `PUT /admin/models/<model_id>/enabled` `{"enabled": false}` |
| Add a new model and make it the default | Insert a `gateway_models` row (see `migrations/002_seed_gateway_config.sql` for the shape), then `PUT /admin/models/<model_id>/default` |
| Change a limit (e.g. raise the monthly cap once traffic looks safe) | `GET /admin/config` to see current values, then `PUT /admin/config/<key>` `{"value": <number>}` |
| See how much one user has used | `GET /admin/users/<user_id>/usage` |
| Turn off a user's hosted-AI access (reversible) | `PUT /admin/users/<user_id>/status` `{"status": "blocked", "reason": "..."}` |
| Permanently remove a user | `DELETE /admin/users/<user_id>` |
| Revoke one of a user's devices | `PUT /admin/devices/<device_id>/status` `{"status": "revoked"}` |
| Pause one feature (e.g. images) while keeping others on | `PUT /admin/feature-flags/alt_text` `{"enabled": false, "reason": "..."}` |
| **Pause everything** (the emergency kill switch) | `PUT /admin/feature-flags/hosted_ai` `{"enabled": false, "reason": "..."}` |
| Check current spend against the budget cap | `GET /admin/spend` |

Every one of these writes an `admin_actions` audit row — "who did what and
when" is always answerable later (`SELECT * FROM admin_actions ORDER BY
created_at DESC`).

## The "start small and learn" philosophy

This service ships with deliberately conservative initial-rollout limits
(100 requests/user/month, a $25/month global budget cap — see PRD §8.1 and
§13 for the full reasoning). **Every one of those numbers is a
`gateway_config` row, not a constant in code** — raising them as the
service proves itself safe in production is a `PUT /admin/config/<key>`
call, never a code change or a redeploy.

## Full API reference

See PRD §24 for the complete request/response contract (every endpoint,
every status code, every error shape) that this codebase implements.
