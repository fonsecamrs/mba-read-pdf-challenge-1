# ADR-003 — Re-ingestion by Replacement with Confirmation

**Status:** Accepted
**Date:** 2026-10-05
**Related requirements:** FR-005, BR-006, DATA-004

## Context

Running the ingestion more than once would duplicate chunks if content were simply appended, and duplicated chunks would take places among the 10 retrieved results. Only one PDF is available at a time (BR-006). Replacing content is destructive, so the user must confirm it.

## Decision

- When the collection already contains chunks, `ingest.py` asks `(s/n)` before replacing them. On `n`, nothing changes.
- On confirmation, all content of the collection is replaced, whether the PDF is the same or a different one.
- Embeddings for the new content are generated **before** the old content is removed. A failure while calling Gemini (e.g., usage limit) leaves the previous content intact.
- With an empty collection (first run, e.g., the evaluator), no question is asked.

## Alternatives Considered

| Alternative | Why not chosen |
| --- | --- |
| Append (accumulate) | Duplicated chunks pollute the top 10 results. |
| Detect an unchanged PDF by file hash and skip | Extra control logic not needed for the scope. Kept as future decision DF-01. |
| Replace without asking | Destructive without confirmation. |
| Ask, but allow skipping with a flag (e.g., `--force`) | Not requested; adds an option to document and test. |

## Consequences

- A second run by the evaluator waits for an answer (R-08, low impact).
- Every confirmed re-ingestion calls the embeddings API again, consuming free tier quota (R-11).
- A failure between removing the old content and storing the new one may leave the collection empty or partial. The user re-runs the ingestion. Accepted as residual risk.
