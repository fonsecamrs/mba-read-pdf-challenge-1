# ADR-001 — Minimal Architecture with Three Entry Scripts

**Status:** Accepted
**Date:** 2026-10-05
**Related requirements:** NFR-001, NFR-003

## Context

The challenge fixes the file structure (`src/ingest.py`, `src/search.py`, `src/chat.py`) and the main flows. The project is an MBA deliverable, evaluated by running it locally. The scope is small: one PDF, one user, no API, no authentication.

A layered architecture (ports and adapters) would allow swapping the LLM provider or the vector store by changing a single adapter, but adds abstractions that this scope does not need.

## Decision

Keep a minimal, direct architecture, faithful to the challenge statement:

- `src/ingest.py`: load PDF → split → embed → store.
- `src/search.py`: retrieval, context and prompt building, LLM call and answer normalization.
- `src/chat.py`: terminal loop only.
- A small settings module outside the mandatory structure (e.g., `src/config.py`) reads and validates `.env`, shared by the three scripts.
- A small errors module (`src/errors.py`) translates library exceptions (Gemini, database) into the user-facing messages and error codes of specs 001 and 002, shared by ingestion and chat.
- LangChain classes are used directly, without interfaces or adapters.

## Alternatives Considered

| Alternative | Why not chosen |
| --- | --- |
| Ports and adapters (hexagonal) with domain layer | More code and concepts than the scope requires; moves away from the simplicity of the statement. |
| Everything inside the three scripts, without a settings module | Duplicates `.env` reading and validation in three places. |

## Consequences

- Fast to implement and easy for the evaluator to read.
- Changing the provider (e.g., Gemini → another) requires editing `ingest.py` and `search.py`. Accepted: the provider is fixed by the challenge.
- Model names and credentials remain in `.env` (NFR-003), so model changes need no code change.
- New abstractions require a new ADR (`CLAUDE.md`, section Restrições).
