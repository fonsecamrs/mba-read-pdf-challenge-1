# Spec 001 — PDF Ingestion

**Status:** Draft
**Entry point:** `src/ingest.py`
**Requirements:** FR-001 to FR-005, BR-006, NFR-003, NFR-005 to NFR-007, SEC-001, SEC-004, DATA-001 to DATA-004 (`docs/prd/PRD.md`)
**Decisions:** ADR-001, ADR-002, ADR-003 (`docs/adr/`)

## 1. Objective

Read a local PDF, split its text into chunks, convert each chunk into an embedding and store everything in PostgreSQL with pgVector, so the chat (spec 002) can retrieve relevant chunks.

## 2. Scope

**In scope:** one PDF per run; replacement of previously ingested content after confirmation; friendly error messages.

**Out of scope:** multiple PDFs at the same time; skipping ingestion when the PDF did not change (DF-01); OCR of scanned PDFs.

## 3. Actors

- **User:** runs `python src/ingest.py` in the terminal.
- **Google Gemini API:** generates the embeddings.
- **PostgreSQL + pgVector:** stores chunks and embeddings.

## 4. Preconditions

- The database container is running (`docker compose up -d`).
- `.env` exists, with a valid `GOOGLE_API_KEY` and the variables listed in `docs/project/phase-1-infrastructure.md`.
- The PDF exists at `PDF_PATH` (default: `document.pdf`).

## 5. Main Flow

1. Load the settings from `.env` and validate the required variables.
2. Load the PDF from `PDF_PATH`, one document per page, keeping the `source` and `page` metadata.
3. Split the text into chunks of **1000 characters** with an overlap of **150 characters** (FR-002).
4. Check whether the configured collection already contains chunks. If it does, run alternative flow A1 before continuing.
5. Generate the embeddings for all chunks (FR-003), applying the retry policy for usage limits (NFR-005).
6. Remove the previously ingested content, if any (BR-006).
7. Store the chunks, their embeddings and their metadata in the collection (FR-004).
8. Display: `Ingestão concluída: {chunks} trechos gravados a partir de {pages} páginas.`

Embeddings are generated (step 5) **before** existing content is removed (step 6), so a failure while calling Gemini leaves the previous content intact (ADR-003).

## 6. Alternative Flows

**A1 — Content already ingested (FR-005)**

1. Display: `Já existe um documento ingerido na base. Deseja substituí-lo? (s/n): `
2. Accepted answers (case-insensitive, surrounding spaces ignored):
   - `s` or `sim`: continue with the main flow at step 5.
   - `n`, `nao` or `não`: display `Ingestão cancelada. Nenhum dado foi alterado.` and exit with code 0.
   - Any other input, including empty: show the question again.
3. Ctrl+C during the question: same as `n`.

**A2 — Usage limit reached (NFR-005)**

1. Embeddings are requested in batches of 50 chunks. When Gemini rejects a batch due to usage limits (HTTP 429), display `Limite de uso da API do Gemini atingido. Nova tentativa em {s} segundos...`, wait and retry only that batch.
2. Waits: 30, 60 and 60 seconds (3 retries after the first attempt), adding up to more than the one-minute limit window (DF-03). The Gemini embeddings client does not retry on its own.
3. If all attempts fail, follow exception E5.

## 7. Exceptions

All messages are displayed in Portuguese without stack traces. With `DEBUG=true`, the technical detail is also printed in English, prefixed by the error code (NFR-006). The process exits with a non-zero code.

| ID | Error code | Situation | Message to the user |
| --- | --- | --- | --- |
| E1 | `config.missing_variable` | A required `.env` variable is missing | `A variável {name} não está configurada no arquivo .env.` |
| E1b | `config.invalid_variable` | A `.env` variable has an invalid value (e.g., non-numeric port) | `A variável {name} tem um valor inválido no arquivo .env.` |
| E2 | `ingestion.pdf_not_found` | The file at `PDF_PATH` does not exist | `Arquivo PDF não encontrado: {path}` |
| E3 | `ingestion.pdf_no_text` | No text could be extracted (e.g., scanned PDF) | `Não foi possível extrair texto do PDF. Verifique se ele não é um documento escaneado.` |
| E4 | `database.unavailable` | The database cannot be reached | `Não foi possível conectar ao banco de dados. Verifique se o Docker está em execução (docker compose up -d).` |
| E5 | `llm.rate_limited` | Usage limit persists after all retries | `O limite de uso da API do Gemini foi atingido. Aguarde alguns minutos e tente novamente.` |
| E6 | `llm.auth_failed` | Invalid API key or missing permission | `A API Key do Gemini é inválida ou não tem permissão de acesso.` |
| E7 | `unexpected` | Any other error | `Ocorreu um erro inesperado. Execute novamente com DEBUG=true para ver os detalhes.` |

## 8. Business Rules

- **BR-006:** only one PDF is available at a time. A confirmed ingestion replaces all previous content, even when the new PDF is a different file.
- Chunk size and overlap are fixed by the challenge and are not configurable.

## 9. Data and Persistence

- Tables are created and managed by LangChain `PGVector` (DATA-001). The project does not create its own tables.
- Each stored chunk contains: text, embedding, and metadata `source` (file path) and `page`.
- The collection name comes from `PG_VECTOR_COLLECTION_NAME`.
- The `vector` extension is enabled by `docs/database/001-create-vector-extension.sql` (DATA-002).
- The embedding dimension is defined by the embeddings model. Changing the model requires re-ingesting with replacement (see `CLAUDE.md`, section Modelos).

## 10. Security and Privacy

- The API key is read from `.env`, which is never committed (SEC-001).
- The PDF content is sent to the Gemini API free tier. The README warns against ingesting sensitive content (SEC-004).

## 11. Acceptance Criteria

| ID | Criterion |
| --- | --- |
| AC-001-1 | With an empty database, the ingestion stores the chunks without asking for confirmation and displays the summary message. |
| AC-001-2 | With content already ingested, the ingestion asks for confirmation. On `s`, the old content is replaced (no duplicated chunks). On `n`, nothing changes. |
| AC-001-3 | A missing PDF, missing variable or stopped database produces the corresponding message from section 7, without a stack trace. |
| AC-001-4 | With `DEBUG=true`, the technical detail and the error code are displayed. |
| AC-001-5 | If the embedding generation fails, previously ingested content remains available to the chat. |

## 12. Unit Test Cases (pytest, no external calls)

| ID | Case |
| --- | --- |
| UT-001-1 | The text splitter is configured with `chunk_size=1000` and `chunk_overlap=150`. |
| UT-001-2 | Confirmation parsing: `s`, `S`, ` sim ` → yes; `n`, `não`, `NAO` → no; `x`, empty → invalid (ask again). |
| UT-001-3 | A missing required variable raises the `config.missing_variable` error naming the variable. |
| UT-001-4 | A non-existent `PDF_PATH` raises `ingestion.pdf_not_found`. |

## 13. Dependencies

- Phase 1: database container, `.env.example`, `requirements.txt`, settings module, chosen embeddings model (ADR-002).
- Final PDF availability (P-001). Development may use a temporary test PDF.
