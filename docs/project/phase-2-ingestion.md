# Phase 2 — PDF Ingestion

**Branch:** `phase-2-ingestion`
**Status:** Not started
**Spec:** `specs/001-pdf-ingestion/spec.md`
**Requirements:** FR-001 to FR-005, BR-006, NFR-005 to NFR-007, DATA-001
**Decisions:** ADR-003
**Pre-requisites:** Phase 1 merged; a PDF available (final PDF, or a temporary test PDF while P-001 is open).

## Goal

Implement `src/ingest.py` according to spec 001.

## Scope and Deliverables

- Main flow, alternative flows A1 (confirmation) and A2 (retries), exceptions E1 to E7.
- **DF-03:** define retry count and wait time from the current free tier limits, and check whether the LangChain integration already retries on its own (avoid double retries).
- Check, in the installed `langchain-postgres` version, how to replace the collection content and how to store pre-computed embeddings (ADR-003: embed before removing).
- Unit tests UT-001-1 to UT-001-4.
- README: ingestion section.

## Acceptance Criteria

- AC-001-1 to AC-001-5 (spec 001), checked manually.
- `pytest` and `ruff check .` pass.

## Risks

- R-02 / R-11: free tier limits during ingestion and repeated re-ingestions.
- R-04: scanned PDF without extractable text (covered by E3).

## Expected Result

The PDF stored in the database, with safe re-ingestion.
