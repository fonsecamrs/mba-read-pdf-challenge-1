# ADR-002 — Gemini Models for Embeddings and LLM

**Status:** Accepted
**Date:** 2026-10-06
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

Official documentation consulted on 2026-10-06:
[models](https://ai.google.dev/gemini-api/docs/models),
[pricing](https://ai.google.dev/gemini-api/docs/pricing),
[deprecations](https://ai.google.dev/gemini-api/docs/deprecations),
[embeddings](https://ai.google.dev/gemini-api/docs/embeddings).

| Use | Model | Status | Free tier | Shutdown |
| --- | --- | --- | --- | --- |
| LLM | `gemini-3.5-flash-lite` | Stable; described as the most cost-effective 3.5 model | Yes | Not announced |
| Embeddings | `gemini-embedding-2` | Stable; official replacement for `gemini-embedding-001` | Yes | Not announced |

- **Embedding dimension:** model default, **3072**. No `output_dimensionality` is configured.
- Both models are supported by `langchain-google-genai` 4.4.0 (the library's own examples use the Gemini Embedding 2 family).

## Alternatives Considered

| Alternative | Why not chosen |
| --- | --- |
| `gemini-3.1-flash-lite` | Slightly cheaper in the paid tier, but shutdown scheduled for 2027-05-07. |
| `gemini-embedding-001` | Older model, replaced by `gemini-embedding-2`, shutdown scheduled for 2028-05-14, no longer listed on the pricing page. |
| Reduced dimension (768) | Smaller vectors, irrelevant for a single PDF; would add one more variable to `.env`. |

## Consequences

- Model names go to `.env` / `.env.example` (`GOOGLE_EMBEDDING_MODEL`, `GOOGLE_LLM_MODEL`).
- Changing the embeddings model after the first ingestion requires a confirmed re-ingestion (destructive operation). Embeddings from different models are not comparable.
- Free tier rate limits are no longer published in the documentation; they are shown only in [Google AI Studio](https://aistudio.google.com/rate-limit) for each account. DF-03 (retries) is decided in phase 2 with those values.
- pgVector approximate indexes (HNSW/IVFFlat) do not support 3072 dimensions on the `vector` type. Not an issue: no index is used (exact search is instant for a single PDF).
