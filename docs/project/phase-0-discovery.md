# Phase 0 — Discovery and Documentation

**Branch:** `phase-0-discovery`
**Status:** In progress

## Goal

Turn the challenge statement into a reviewed set of requirements, specs, decisions and phases, and prepare the repository.

## Scope and Deliverables

- Git repository initialized, connected to `origin`, with `.gitignore` and `.gitattributes`.
- `docs/prd/PRD.md` v2 (approved).
- `CLAUDE.md` adapted to the project.
- Specs: `specs/001-pdf-ingestion/spec.md`, `specs/002-semantic-chat/spec.md`.
- ADRs: ADR-001 (architecture), ADR-002 (models, pending), ADR-003 (re-ingestion), ADR-004 (fallback normalization).
- Phase documents: `docs/project/phase-0` to `phase-4`.

## Acceptance Criteria

- All documents reviewed and approved by the project owner.
- Every requirement in the PRD is referenced by at least one spec or phase.
- No secrets in the repository.

## Risks

- Documentation larger than the code (R-09). Mitigation: lean documentation, only what guides implementation.

## Expected Result

Phase 1 can start without open questions other than those registered as pending or future decisions in the PRD (section 11).
