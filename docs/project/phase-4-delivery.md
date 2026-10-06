# Phase 4 — Delivery

**Branch:** `phase-4-delivery`
**Status:** Not started
**Requirements:** NFR-009, SEC-001, SEC-004
**Pre-requisites:** Phases 1 to 3 merged; final PDF available (P-001, P-002 closed).

## Goal

Make sure the evaluator can clone the public repository and run everything using only the README.

## Scope and Deliverables

- Final `README.md` in Portuguese: requirements, setup (Windows and Linux/macOS), `.env` configuration, execution, example session, free tier warning (SEC-004), troubleshooting (database not running, port in use, rate limit).
- Final `document.pdf` in the project root.
- Validation from a clean clone: new folder, new virtual environment, new `.env` from `.env.example`, empty database volume.
- Full manual acceptance script (specs 001 and 002).
- Final check that no secret was committed (git history included).
- Merge into `main` and push (with the owner's permission).

## Acceptance Criteria

- A clean clone runs end-to-end by following only the README.
- All PRD acceptance scenarios (A to G) pass.
- `pytest` and `ruff check .` pass.

## Risks

- Differences between the development machine (Windows) and the evaluator's machine.

## Expected Result

Challenge delivered: public repository link ready to submit.
