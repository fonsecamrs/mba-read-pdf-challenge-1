# ADR-005 — Keep PyPDFLoader Despite the langchain-community Sunset

**Status:** Accepted
**Date:** 2026-10-06
**Related requirements:** FR-001, NFR-001

## Context

The challenge recommends `PyPDFLoader` from `langchain_community.document_loaders`. The `langchain-community` package was [sunset on 2026-05-22](https://github.com/langchain-ai/langchain-community/issues/674) and its repository archived: no new fixes. Version 0.4.2 still installs and works on Python 3.14, but importing it emits a `DeprecationWarning` that would appear in the user's terminal.

No official standalone package replaces `PyPDFLoader`. The community alternative based on PyMuPDF is AGPL-licensed.

## Decision

- Keep `PyPDFLoader` from `langchain-community==0.4.2`, as recommended by the challenge.
- Silence only this `DeprecationWarning` in `src/ingest.py`, at import time, with a comment pointing to this ADR.

## Alternatives Considered

| Alternative | Why not chosen |
| --- | --- |
| Read the PDF with `pypdf` directly (~10 lines) | Removes the sunset package, but diverges from the package recommended by the challenge. Remains the fallback if `langchain-community` stops working. |
| PyMuPDF-based loader | AGPL license; heavier dependency. |

## Consequences

- The pinned version keeps working; it receives no fixes.
- If a future dependency update breaks `langchain-community`, replace the loader with `pypdf` directly (same library used by `PyPDFLoader` underneath). Only `src/ingest.py` changes.
