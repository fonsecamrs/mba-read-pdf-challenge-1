# Spec 002 — Semantic Search & Chat

**Status:** Draft
**Entry points:** `src/chat.py` (terminal interaction), `src/search.py` (retrieval, prompt and LLM call)
**Requirements:** FR-006 to FR-011, BR-001 to BR-005, BR-007, BR-008, NFR-003, NFR-006, NFR-007 (`docs/prd/PRD.md`)
**Decisions:** ADR-001, ADR-002, ADR-004 (`docs/adr/`)

## 1. Objective

Let the user ask questions in Portuguese in the terminal and receive answers based **only** on the ingested PDF, or the exact fallback phrase when the PDF does not contain the answer.

## 2. Scope

**In scope:** question loop, retrieval of 10 chunks, fixed prompt, LLM call, fallback normalization, exit commands, friendly errors.

**Out of scope:** conversation memory, displaying sources, score filtering, persistence of questions or answers.

## 3. Actors

- **User:** runs `python src/chat.py` and types questions.
- **Google Gemini API:** embeds the question and generates the answer.
- **PostgreSQL + pgVector:** returns the most similar chunks.

## 4. Preconditions

- The database container is running and a PDF has been ingested (spec 001).
- `.env` is configured with the same embeddings model used in the ingestion.

## 5. Responsibilities per File

| File | Responsibility |
| --- | --- |
| `src/chat.py` | Terminal loop: prompts, labels, exit commands, empty input, display of answers and errors. No LangChain calls. |
| `src/search.py` | Checks whether content was ingested, retrieves the chunks, builds the context and the prompt, calls the LLM and normalizes the answer. Exposes one entry function for `chat.py` (e.g., `answer_question(question) -> str`) plus pure helper functions that are unit tested. |

## 6. Main Flow

1. Load the settings from `.env`.
2. Check that the collection contains ingested chunks. If not, follow alternative flow A3.
3. Display `Faça sua pergunta:` followed by a blank line.
4. Read the question on a line prefixed by `PERGUNTA: `.
5. Trim the input. If it is empty, go back to step 4 (FR-010). If it is an exit command, follow A1.
6. Retrieve the 10 most relevant chunks with `similarity_search_with_score(query, k=10)` (FR-007). The scores are not used to filter (BR-004).
7. Build the context: the text of each chunk, in the returned order, separated by one blank line, with no added metadata (BR-005).
8. Build the prompt from the canonical template in `CLAUDE.md`, section "Requisitos funcionais fixos", replacing **only** the two placeholders (FR-008):
   - `{resultados concatenados do banco de dados}` → context from step 7;
   - `{pergunta do usuário}` → trimmed question.
   The replacement is literal (string replace), so braces typed by the user never break the template.
9. Send the prompt to the LLM, without sampling parameters (the chosen model ignores them; ADR-002). If Gemini is temporarily overloaded (HTTP 5xx), steps 6 to 9 are retried silently after 2 and 5 seconds; usage limits (HTTP 429) are not retried.
10. Normalize the answer (BR-003, section 8).
11. Display `RESPOSTA: {answer}`, followed by a blank line, and go back to step 3.

Example session:

```text
Faça sua pergunta:

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

Faça sua pergunta:

PERGUNTA: Qual é a capital da França?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.

Faça sua pergunta:

PERGUNTA: sair
Até logo!
```

## 7. Alternative Flows

**A1 — Exit (FR-009):** the input `sair` (case-insensitive, surrounding spaces ignored) displays `Até logo!` and exits with code 0.

**A2 — Interruption (FR-009):** Ctrl+C or end of input (Ctrl+D / Ctrl+Z), at any moment, including while waiting for the LLM, displays `Até logo!` and exits with code 0, without a stack trace.

**A3 — Nothing ingested (FR-011, error code `chat.no_content`):** display `Nenhum documento foi ingerido. Execute primeiro: python src/ingest.py` and exit with a non-zero code.

## 8. Fallback Normalization (BR-002, BR-003, ADR-004)

Canonical phrase: `Não tenho informações necessárias para responder sua pergunta.`

The answer is replaced by the canonical phrase **only** when, after the steps below, it is equal to the canonical phrase without its final period:

1. Trim surrounding whitespace.
2. Remove a leading `Resposta:` label (case-insensitive), if present.
3. Remove surrounding quotes (`"`, `'`, `“`, `”`).
4. Remove a trailing period.
5. Compare case-insensitively.

Any other answer is displayed unchanged, even if it contains the canonical phrase as part of a longer text (risk R-10).

## 9. Exceptions

Messages are displayed in Portuguese without stack traces; with `DEBUG=true` the technical detail is also printed in English with the error code (NFR-006). Errors at startup (before the first question) end the chat with a non-zero code. Errors during a question do not end the chat: the message is shown in place of the answer and the loop continues.

| ID | Error code | Situation | Message to the user |
| --- | --- | --- | --- |
| E1 | `config.missing_variable` | A required `.env` variable is missing | `A variável {name} não está configurada no arquivo .env.` |
| E1b | `config.invalid_variable` | A `.env` variable has an invalid value (e.g., non-numeric port) | `A variável {name} tem um valor inválido no arquivo .env.` |
| E2 | `database.unavailable` | The database cannot be reached | `Não foi possível conectar ao banco de dados. Verifique se o Docker está em execução (docker compose up -d).` |
| E3 | `llm.rate_limited` | Gemini usage limit reached (reported immediately, no retry) | `O limite de uso da API do Gemini foi atingido. Aguarde alguns minutos e tente novamente.` |
| E3b | `llm.unavailable` | Gemini overloaded (HTTP 5xx) after the quick retries | `O serviço do Gemini está sobrecarregado no momento. Tente novamente em instantes.` |
| E4 | `llm.auth_failed` | Invalid API key or missing permission | `A API Key do Gemini é inválida ou não tem permissão de acesso.` |
| E5 | `unexpected` | Any other error | `Ocorreu um erro inesperado. Execute novamente com DEBUG=true para ver os detalhes.` |

## 10. Business Rules

- **BR-001 / BR-002:** enforced by the fixed prompt and by the normalization in section 8.
- **BR-004:** always 10 chunks (or fewer, if the collection has fewer than 10).
- **BR-007:** only `PERGUNTA:` / `RESPOSTA:`; no sources, scores or extra information.
- Each question is independent: no previous question or answer is sent to the LLM.

## 11. Data and Persistence

Read-only access to the collection created by spec 001. Nothing is written to the database or to files.

## 12. Security and Privacy

- The question and the retrieved chunks are sent to the Gemini API free tier (SEC-004).
- Prompt injection (e.g., "ignore as regras") is an accepted residual risk (R-13): local single user, no sensitive data.

## 13. Acceptance Criteria (manual script, end of phase 3)

| ID | Question | Expected answer |
| --- | --- | --- |
| AC-002-1 | A question answered by the PDF (Scenario A) | Factually consistent with the PDF |
| AC-002-2 | `Quantos clientes temos em 2024?` | Exactly the canonical phrase |
| AC-002-3 | `Qual é a capital da França?` | Exactly the canonical phrase |
| AC-002-4 | `Você acha isso bom ou ruim?` | Exactly the canonical phrase |
| AC-002-5 | Empty input | Prompt shown again, no API call |
| AC-002-6 | `sair`, `SAIR`, Ctrl+C | `Até logo!`, no stack trace |
| AC-002-7 | Chat started with an empty collection | Message A3 and exit |
| AC-002-8 | Chat started with the database stopped | Message E2 and exit |

Questions for AC-002-1 are defined once the final PDF is available (P-001).

## 14. Unit Test Cases (pytest, no external calls)

| ID | Case |
| --- | --- |
| UT-002-1 | Context building joins chunk texts with one blank line, in order, without metadata. |
| UT-002-2 | Prompt building replaces both placeholders and leaves no other part of the template changed. |
| UT-002-3 | A question containing `{` and `}` is inserted literally without errors. |
| UT-002-4 | Normalization: `"Não tenho informações necessárias para responder sua pergunta."` (with quotes), the phrase without period, with extra spaces, and with a `Resposta:` prefix → canonical phrase. |
| UT-002-5 | Normalization keeps unchanged: a factual answer; a longer text that contains the canonical phrase. |
| UT-002-6 | Exit command detection: `sair`, ` SAIR ` → exit; `sair agora`, empty → not exit. |

## 15. Dependencies

- Spec 001 (ingested collection).
- Phase 1: settings module and chosen LLM model (ADR-002).
