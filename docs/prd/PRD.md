# Product Requirements Document (PRD)

**Project:** PDF Semantic Search & Ingestion CLI (MBA IA Full Cycle - Challenge 1)
**Document Status:** Approved (v2)
**Last Update:** 2026-10-05

## 1. Product Overview

The objective of this project is to build a Command Line Interface (CLI) application capable of ingesting a PDF document into a vector database and allowing users to query the document's content via semantic search (RAG). The system must act as a strict Q&A assistant that relies **exclusively** on the ingested PDF context to answer user questions, strictly preventing AI hallucinations.

The project is an MBA challenge deliverable. It is delivered as a public GitHub repository, and an evaluator clones it and runs it locally by following the README.

## 2. Target Audience & Use Cases

- **Target User:** A single local user interacting via the terminal (in practice, the developer and the challenge evaluator). There are no user profiles, roles or authentication.
- **Primary Need:** Extract specific factual information from a dense PDF document without reading it entirely, trusting that the AI will not invent information.

| ID | Use Case |
| --- | --- |
| UC-01 | Ingest the PDF into the database |
| UC-02 | Re-ingest the PDF or replace it with another PDF |
| UC-03 | Ask a question answered by the PDF content |
| UC-04 | Ask a question not answered by the PDF content |
| UC-05 | End the chat session |

## 3. Scope

### In Scope

- Ingestion of one local PDF at a time.
- A terminal chat that answers questions based only on the ingested PDF.

### Out of Scope

- Authentication, authorization or multiple users.
- HTTP APIs, web or graphical interfaces.
- Querying multiple PDFs at the same time.
- Conversation memory between questions (each question is independent).
- Displaying sources (pages) in the answer.
- Persisting user questions and answers, or writing logs to files.
- Remote deployment. The system runs only on the user's machine.

## 4. Functional Requirements

### Feature 1: PDF Document Ingestion (`src/ingest.py`)

| ID | Requirement |
| --- | --- |
| FR-001 | The system must read the PDF located at the path configured in `PDF_PATH`, defaulting to `document.pdf` in the project root. |
| FR-002 | The text must be split into chunks of 1000 characters with an overlap of 150 characters. |
| FR-003 | Each chunk must be converted into an embedding using a Google Gemini embeddings model. |
| FR-004 | Chunks and embeddings must be stored in PostgreSQL with pgVector. |
| FR-005 | If the database already contains ingested content, the system must ask the user for confirmation (`s/n`) before replacing it. On `s`, all existing content is replaced. On `n`, the ingestion ends without changing anything. |

### Feature 2: Semantic Search & Q&A CLI (`src/search.py`, `src/chat.py`)

| ID | Requirement |
| --- | --- |
| FR-006 | The chat must open with `Faça sua pergunta:` and display each interaction with the labels `PERGUNTA:` and `RESPOSTA:`. |
| FR-007 | The system must vectorize the question and retrieve the 10 most relevant chunks (`similarity_search_with_score(query, k=10)`). |
| FR-008 | The system must build the challenge prompt template verbatim, filling only its two placeholders (retrieved context and user question), and send it to a Google Gemini LLM. |
| FR-009 | Typing `sair` must end the chat with a farewell message. Pressing Ctrl+C must also end it without displaying a technical error. |
| FR-010 | An empty input must be ignored without calling any external API, and the question prompt must be shown again. |
| FR-011 | If no document has been ingested, the chat must inform the user that the ingestion must be run first and then exit. |

## 5. Business Rules & Guardrails

| ID | Rule |
| --- | --- |
| BR-001 | **Strict Context Confinement (No Hallucination):** The LLM must *never* use external knowledge, formulate opinions, or interpret beyond what is written in the retrieved context. |
| BR-002 | **Fallback Answer:** If the information is not explicitly found in the context, the answer must be exactly: `Não tenho informações necessárias para responder sua pergunta.` |
| BR-003 | **Fallback Normalization:** When the LLM answer is essentially the fallback phrase with formatting variations (quotes, spaces, punctuation), the system must display the exact phrase defined in BR-002. Valid answers that are not the fallback phrase must never be replaced. |
| BR-004 | **Retrieval Metric:** All 10 retrieved chunks must always be sent to the LLM, without filtering by similarity score. |
| BR-005 | **Context Format:** The retrieved chunks are concatenated as plain text, separated by a blank line, with no added metadata. |
| BR-006 | **Single Document:** Only one PDF is available for querying at a time. A new ingestion replaces all previous content. |
| BR-007 | **Answer Format:** The output contains only the `PERGUNTA:` / `RESPOSTA:` format, without sources or extra information. |
| BR-008 | **Language Boundaries:** AI prompts, end-user messages and the README: Portuguese (PT-BR). Codebase, technical documentation, error codes and technical logs: English. |

## 6. Non-Functional Requirements

| ID | Requirement |
| --- | --- |
| NFR-001 | **Stack:** Python and LangChain, keeping the mandatory file structure defined by the challenge. |
| NFR-002 | **Database:** PostgreSQL with pgVector, run via Docker Compose, with data persisted in a Docker volume. |
| NFR-003 | **Configuration:** API key, model names, database connection, collection name, `PDF_PATH` and `DEBUG` are configured through `.env`, with a template kept in `.env.example`. Models are not hard-coded. Sampling parameters (temperature, top_p, top_k) are not used: the chosen LLM ignores them and Google deprecated them (ADR-002). |
| NFR-004 | **Model Choice:** The lightest and cheapest Gemini models currently available must be chosen, based on Google's official documentation. |
| NFR-005 | **Rate Limits and Overload:** During ingestion, when Gemini rejects a request due to usage limits or temporary overload, the system must wait and retry a limited number of times, then stop with a clear message. In the chat, usage limits are reported immediately, and temporary overload is retried a couple of times quickly before a clear message. |
| NFR-006 | **Error Handling:** Errors are shown to the user as friendly Portuguese messages, without stack traces. With `DEBUG=true`, technical details (in English) are also displayed. |
| NFR-007 | **Logging:** Technical logs are written only to the terminal, when `DEBUG=true`. |
| NFR-008 | **Quality:** Deterministic parts are covered by unit tests (pytest) that make no external calls. Code style is enforced with ruff. |
| NFR-009 | **Usability:** The README provides setup and execution commands for both Windows and Linux/macOS. |

## 7. Security & Privacy Requirements

| ID | Requirement |
| --- | --- |
| SEC-001 | The `.env` file must never be committed to the repository. |
| SEC-002 | Database credentials are configured through `.env`. `.env.example` provides simple local development values. |
| SEC-003 | The database port must be published only on `127.0.0.1`. |
| SEC-004 | The project uses the Gemini API free tier, under which Google may use submitted content to improve its products. The README must warn users not to ingest PDFs containing sensitive, confidential or personal information. |

## 8. Data Requirements

| ID | Requirement |
| --- | --- |
| DATA-001 | Vector tables are created and managed by the LangChain `PGVector` integration. Each stored chunk contains its text, its embedding and its metadata (source file and page). |
| DATA-002 | The `vector` extension is enabled by a versioned script in `docs/database`. |
| DATA-003 | No personal data and no user questions are persisted. |
| DATA-004 | No backup is required: all stored data can be regenerated by running the ingestion again. |

## 9. Acceptance Criteria

**Scenario A: Question within the PDF context (FR-007, FR-008, BR-001)**
- **Given** the ingested PDF contains the information asked
- **When** the user asks a question about it (e.g., *"Qual o faturamento da Empresa SuperTechIABrazil?"*, if the PDF contains *"O faturamento foi de 10 milhões de reais"*)
- **Then** the CLI must respond with an answer that is factually consistent with the PDF content (e.g., *"O faturamento foi de 10 milhões de reais."*). The exact wording may vary.

**Scenario B: Question outside the PDF context (BR-002, BR-003)**
- **Given** the PDF does not contain customer metrics for 2024
- **When** the user asks: *"Quantos clientes temos em 2024?"*
- **Then** the CLI must respond exactly with: `Não tenho informações necessárias para responder sua pergunta.`

**Scenario C: General knowledge (BR-001, BR-002)**
- **When** the user asks: *"Qual é a capital da França?"*
- **Then** the CLI must respond exactly with: `Não tenho informações necessárias para responder sua pergunta.`

**Scenario D: Opinion request (BR-001, BR-002)**
- **When** the user asks: *"Você acha isso bom ou ruim?"*
- **Then** the CLI must respond exactly with: `Não tenho informações necessárias para responder sua pergunta.`

**Scenario E: Re-ingestion (FR-005, BR-006)**
- **Given** a PDF has already been ingested
- **When** the user runs the ingestion again
- **Then** the system asks for confirmation; on `s` it replaces all content, and on `n` it exits without changes.

**Scenario F: Chat without ingested content (FR-011)**
- **Given** no document has been ingested
- **When** the user starts the chat
- **Then** the system informs that the ingestion must be run first and exits.

**Scenario G: Chat controls (FR-009, FR-010)**
- **When** the user presses Enter without typing, **then** the question prompt is shown again without calling any API.
- **When** the user types `sair` or presses Ctrl+C, **then** the chat ends without a technical error.

## 10. High-Level Technical Constraints

*(Implementation details, architecture decisions and phases are defined in `specs/`, `docs/adr/` and `docs/project/`.)*

- **Core Stack:** Python, LangChain, PostgreSQL + pgVector.
- **LLM/Embeddings:** Google Gemini models, configured through environment variables (no dynamic model selection at runtime).
- **Execution:** Database infrastructure containerized via Docker Compose.

## 11. Open Items

| ID | Type | Description |
| --- | --- | --- |
| P-001 | Pending | The challenge PDF (`document.pdf`) is not yet available. Scenario A cannot be validated with real data until then. |
| P-002 | Pending | Confirm that the PDF contains no sensitive data (depends on P-001). |
| DF-01 | Future decision | Detect an already-ingested PDF (e.g., by file hash) instead of always replacing the content. |
| DF-02 | Resolved (phase 1) | Models: `gemini-3.5-flash-lite` and `gemini-embedding-2` (ADR-002). |
| DF-03 | Resolved (phase 2) | Embeddings in batches of 50, retries after 30, 60 and 60 seconds (spec 001, A2). |
| DF-04 | Resolved (phase 1) | Python 3.14 confirmed; minimum supported version 3.12 (required by `numpy`). |
