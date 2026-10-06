# Product Requirements Document (PRD)
**Project:** PDF Semantic Search & Ingestion CLI (MBA IA FullCycle - Challenge 1)
**Document Status:** Approved

## 1. Product Overview
The objective of this project is to build a Command Line Interface (CLI) application capable of ingesting PDF documents into a vector database and allowing users to query the document's content via semantic search. The system must act as a strict Q&A assistant that relies **exclusively** on the ingested PDF context to answer user questions, strictly preventing AI hallucinations.

## 2. Target Audience & Use Cases
- **Target User:** End-users interacting via the terminal (CLI).
- **Primary Use Case:** A user needs to extract specific factual information, metrics, or summaries from a dense PDF document without reading it entirely, trusting that the AI will not invent information.

## 3. Core Features & Scope

### Feature 1: PDF Document Ingestion
The system must parse a target PDF document, process its text into semantic vectors (embeddings), and store them persistently in a database.
- **Data Source:** A local `.pdf` file.
- **Processing Logic:** Text must be split into chunks to maintain context accuracy.
- **Storage:** Vectorized chunks must be saved into a PostgreSQL database equipped with vector search capabilities.

### Feature 2: Semantic Search & Q&A CLI
A terminal-based chat interface where users can type natural language questions and receive direct answers.
- **Retrieval:** The system must vectorize the user's question and retrieve the most relevant text chunks from the database.
- **Generation:** An LLM will formulate a concise answer based on the retrieved chunks.
- **Language:** The interaction with the end-user (questions and answers) must be in **Portuguese (PT-BR)**.

## 4. Business Rules & Guardrails

- **BR-01: Strict Context Confinement (No Hallucination):** 
  The LLM must *never* use external knowledge, formulate opinions, or interpret beyond what is written. If the information is not explicitly found in the retrieved context, the system must reply with the exact fallback phrase: *"Não tenho informações necessárias para responder sua pergunta."*
- **BR-02: Chunking Strategy:** 
  For precision, text splitting must strictly use 1000 characters per chunk with an overlap of 150 characters.
- **BR-03: Retrieval Metric:** 
  The search query must always retrieve the top 10 most relevant results (`k=10`) from the vector database to build the LLM context.
- **BR-04: Language Boundaries:**
  - AI Prompts and End-User interactions: Portuguese.
  - Codebase, error codes, and technical logs: English.

## 5. Acceptance Criteria

**Scenario A: Question within the PDF context**
- **Given** the PDF contains the phrase "O faturamento foi de 10 milhões de reais"
- **When** the user asks: *"Qual o faturamento da Empresa SuperTechIABrazil?"*
- **Then** the CLI must respond with the correct factual data: *"O faturamento foi de 10 milhões de reais."*

**Scenario B: Question outside the PDF context**
- **Given** the PDF does not contain customer metrics for 2024
- **When** the user asks: *"Quantos clientes temos em 2024?"*
- **Then** the CLI must respond exactly with: *"Não tenho informações necessárias para responder sua pergunta."*

**Scenario C: General Knowledge (Out of Context)**
- **When** the user asks: *"Qual é a capital da França?"*
- **Then** the CLI must respond exactly with: *"Não tenho informações necessárias para responder sua pergunta."*

## 6. High-Level Technical Constraints
*(Note: Detailed implementation steps, architecture decisions, and folder structures are defined in ADRs and `docs/project/`)*
- **Core Stack:** Python, PostgreSQL + pgVector.
- **LLM/Embeddings:** Google Gemini Models (must support dynamic model selection based on current API availability/pricing).
- **Execution:** Database infrastructure must be containerized via Docker.