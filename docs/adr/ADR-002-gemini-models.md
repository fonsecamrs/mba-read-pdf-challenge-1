# ADR-002 — Gemini Models for Embeddings and LLM

**Status:** Pending (to be decided in phase 1)
**Date:** 2026-10-05
**Related requirements:** NFR-003, NFR-004, SEC-004

## Context

The challenge requires Google Gemini for embeddings and for the LLM, but does not fix the models. The project uses the Gemini API free tier, which has request limits per minute and per day. Model availability changes over time, so names must not be assumed from memory (`CLAUDE.md`, section Modelos).

## Decision Criteria

1. Model available in Google's official documentation at decision time, and not marked as deprecated.
2. Available in the free tier.
3. Lightest and cheapest option that meets the requirements.
4. Free tier limits compatible with ingesting the challenge PDF (impacts DF-03).
5. For embeddings: output dimension known and documented, since it is fixed in the database after the first ingestion.
6. Compatible with the `langchain-google-genai` version chosen in phase 1.

## Decision

Pending. To be filled in phase 1 with the chosen models, the date of the consulted documentation, the links used and the embedding dimension.

## Consequences

- Model names go to `.env` / `.env.example` (`GOOGLE_EMBEDDING_MODEL`, `GOOGLE_LLM_MODEL`).
- Changing the embeddings model after the first ingestion requires a confirmed re-ingestion (destructive operation).
