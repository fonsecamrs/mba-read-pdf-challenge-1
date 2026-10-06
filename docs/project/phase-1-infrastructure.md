# Phase 1 — Infrastructure and Configuration

**Branch:** `phase-1-infrastructure`
**Status:** Completed (2026-10-06)

## Decisions Taken (2026-10-06)

- **DF-04:** Python 3.14 confirmed by a test installation of all dependencies. Minimum supported version: 3.12 (required by the pinned `numpy`).
- **DF-02:** `gemini-3.5-flash-lite` and `gemini-embedding-2`, dimension 3072 (ADR-002).
- **Database image:** `pgvector/pgvector:0.8.7-pg18-trixie` (pgvector 0.8.7, PostgreSQL 18). Since PostgreSQL 18, the volume is mounted at `/var/lib/postgresql`.
- **PDF loader:** keep `PyPDFLoader` despite the `langchain-community` sunset (ADR-005).
- **Dependencies:** only direct dependencies pinned in `requirements.txt`; dev tools in `requirements-dev.txt`.
- **Settings:** invalid values (e.g., non-numeric port) raise `config.invalid_variable`, added to specs 001 and 002.
**Requirements:** NFR-001 to NFR-004, NFR-008, SEC-001 to SEC-003, DATA-002
**Pre-requisites:** Phase 0 approved and merged into `main`.

## Goal

Have the database running, the dependencies installable and the settings available, so that ingestion and chat can be implemented.

## Scope and Deliverables

1. **Decisions to make first**
   - **DF-04 — Python version:** check that LangChain, `langchain-google-genai`, `langchain-postgres` and the PostgreSQL driver support Python 3.14 (installed version). If not, document the supported version to install alongside it.
   - **DF-02 — Models:** consult Google's official documentation and fill ADR-002.
   - **Database image:** check the current official pgVector image and pin its tag.
2. **`docker-compose.yml`**
   - PostgreSQL with pgVector, credentials read from `.env` (SEC-002).
   - Port published only on `127.0.0.1` (SEC-003).
   - Named volume for data persistence (NFR-002).
   - `docs/database/` mounted as initialization scripts.
   - Healthcheck, so the evaluator can see when the database is ready.
3. **`docs/database/001-create-vector-extension.sql`** — `CREATE EXTENSION IF NOT EXISTS vector;` (DATA-002).
4. **`requirements.txt`** — runtime dependencies with pinned versions.
5. **Development dependencies** (proposal: `requirements-dev.txt` with pytest and ruff) and tool configuration (proposal: `pyproject.toml` with ruff and pytest settings).
6. **`.env.example`** — all variables below, with local development defaults and no real key.
7. **Settings module** (`src/config.py`, ADR-001) — reads `.env`, applies defaults, validates required variables (`config.missing_variable`) and builds the database URL.
8. **README** — setup section (Windows and Linux/macOS).

## Environment Variables (proposal)

| Variable | Required | Default in `.env.example` | Purpose |
| --- | --- | --- | --- |
| `GOOGLE_API_KEY` | Yes | empty | Gemini API key |
| `GOOGLE_EMBEDDING_MODEL` | Yes | from ADR-002 | Embeddings model |
| `GOOGLE_LLM_MODEL` | Yes | from ADR-002 | Chat model |
| `LLM_TEMPERATURE` | No | `0` | LLM temperature |
| `POSTGRES_USER` | Yes | `postgres` | Database user (also used by Docker Compose) |
| `POSTGRES_PASSWORD` | Yes | `postgres` | Database password (local development only) |
| `POSTGRES_DB` | Yes | `rag` | Database name |
| `POSTGRES_HOST` | No | `127.0.0.1` | Database host (IPv4 address: `localhost` may resolve to IPv6 first on Windows and hang, while the port is published only on IPv4) |
| `POSTGRES_PORT` | No | `5432` | Database port |
| `PG_VECTOR_COLLECTION_NAME` | No | `document_chunks` | Collection name |
| `PDF_PATH` | No | `document.pdf` | PDF to ingest |
| `DEBUG` | No | `false` | Shows technical details and logs |

## Acceptance Criteria

- `docker compose up -d` starts the database and the healthcheck reports it healthy.
- The `vector` extension is enabled in the database.
- `pip install -r requirements.txt` (and the dev requirements) completes without errors on the chosen Python version.
- The database is not reachable from other machines (port bound to `127.0.0.1`).
- `ruff check .` and `pytest` run (even with no tests yet).
- ADR-002 filled with models, documentation date and links.

## Tests

- UT-001-3 (missing variable) can be implemented in this phase, together with the settings module.

## Risks

- R-12: dependencies without Python 3.14 support.
- Port 5432 already in use on the evaluator's machine. Mitigation: `POSTGRES_PORT` configurable.

## Expected Result

A reproducible local environment, documented in the README, ready for phases 2 and 3.
