# ADR-004 — Normalization of the Fallback Answer in Code

**Status:** Accepted
**Date:** 2026-10-05
**Related requirements:** BR-002, BR-003

## Context

When the PDF does not answer the question, the answer must be exactly `Não tenho informações necessárias para responder sua pergunta.` The fixed prompt shows this phrase between quotes and in examples prefixed by `Resposta:`, so the LLM may return it with quotes, a prefix, extra spaces or without the final period. The prompt text cannot be changed.

## Decision

`search.py` normalizes the LLM answer: after trimming spaces, removing a leading `Resposta:` label, surrounding quotes and a trailing period, if the result is equal (case-insensitive) to the canonical phrase without its period, the canonical phrase is displayed. The exact steps are in spec 002, section 8.

## Alternatives Considered

| Alternative | Why not chosen |
| --- | --- |
| Trust only the prompt | Formatting variations would fail acceptance scenarios B, C and D. |
| Replace any answer containing the phrase | Could replace legitimate answers (risk R-10). |
| Structured output (JSON with an "answered" flag) | Requires changing the prompt, which is forbidden. |

## Consequences

- Scenarios B, C and D become robust to formatting variations.
- Semantic variations (e.g., a different sentence with the same meaning) are not normalized. Mitigated by temperature `0` (NFR-003).
- Covered by unit tests UT-002-4 and UT-002-5.
