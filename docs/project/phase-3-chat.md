# Phase 3 — Semantic Search and Chat

**Branch:** `phase-3-chat`
**Status:** Not started
**Spec:** `specs/002-semantic-chat/spec.md`
**Requirements:** FR-006 to FR-011, BR-001 to BR-005, BR-007, BR-008, NFR-006, NFR-007
**Decisions:** ADR-004
**Pre-requisites:** Phase 2 merged; content ingested.

## Goal

Implement `src/search.py` and `src/chat.py` according to spec 002.

## Scope and Deliverables

- `search.py`: ingestion check, retrieval (`k=10`), context, prompt from the canonical template in `CLAUDE.md`, LLM call, normalization.
- `chat.py`: loop, labels, `sair`, Ctrl+C / end of input, empty input, error display.
- Unit tests UT-002-1 to UT-002-6.
- Manual acceptance script with the final PDF questions (AC-002-1 to AC-002-8).
- README: chat section and example session.

## Acceptance Criteria

- AC-002-1 to AC-002-8 (spec 002), checked manually and recorded.
- PRD scenarios A, B, C, D, F and G pass.
- `pytest` and `ruff check .` pass.

## Risks

- R-06 / R-10: fallback phrase variations and over-normalization (covered by UT-002-4 and UT-002-5).
- P-001: without the final PDF, AC-002-1 can only be checked with a test PDF.
- R-13: prompt injection, accepted.

## Expected Result

A working chat that answers only from the PDF.
