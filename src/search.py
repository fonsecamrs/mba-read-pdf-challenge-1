"""Semantic search: retrieve relevant chunks, build the fixed prompt and ask the LLM (spec 002)."""

import re

from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import Settings
from errors import is_server_error, run_with_retries

# Number of chunks sent to the LLM, fixed by the challenge (FR-007, BR-004)
TOP_K = 10

# Quick silent retries when Gemini is temporarily overloaded (5xx). Usage limits (429) are
# not retried: the user is told immediately (spec 002, E3).
OVERLOAD_WAITS_SECONDS = (2, 5)

FALLBACK_ANSWER = "Não tenho informações necessárias para responder sua pergunta."

CONTEXT_PLACEHOLDER = "{resultados concatenados do banco de dados}"
QUESTION_PLACEHOLDER = "{pergunta do usuário}"

# Canonical text: CLAUDE.md, section "Requisitos funcionais fixos". Do not change it.
PROMPT_TEMPLATE = """CONTEXTO:
{resultados concatenados do banco de dados}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta do usuário}

RESPONDA A "PERGUNTA DO USUÁRIO\""""

PLACEHOLDER_PATTERN = re.compile(
    f"{re.escape(CONTEXT_PLACEHOLDER)}|{re.escape(QUESTION_PLACEHOLDER)}"
)

ANSWER_LABEL_PATTERN = re.compile(r"^resposta:\s*", re.IGNORECASE)
QUOTES = "\"'“”"

# Markdown the LLM may use, which a terminal would show as raw symbols
MARKDOWN_BOLD_PATTERN = re.compile(r"\*\*(.+?)\*\*|__(.+?)__", re.DOTALL)
MARKDOWN_ITALIC_PATTERN = re.compile(r"(?<![\w*])\*(?=\S)([^*\n]+?)(?<=\S)\*(?![\w*])")
MARKDOWN_BULLET_PATTERN = re.compile(r"^(\s*)[*+]\s+", re.MULTILINE)
MARKDOWN_HEADING_PATTERN = re.compile(r"^#{1,6}\s+", re.MULTILINE)
EXTRA_BLANK_LINES_PATTERN = re.compile(r"\n{3,}")

COUNT_CHUNKS_SQL = text(
    """
    SELECT count(*)
    FROM langchain_pg_embedding e
    JOIN langchain_pg_collection c ON c.uuid = e.collection_id
    WHERE c.name = :name
    """
)


def count_chunks(engine: Engine, collection_name: str) -> int:
    with engine.connect() as connection:
        return connection.execute(COUNT_CHUNKS_SQL, {"name": collection_name}).scalar_one()


def build_context(results: list[tuple[Document, float]]) -> str:
    """Chunk texts in the returned order, separated by a blank line, without metadata (BR-005)."""
    return "\n\n".join(document.page_content for document, _score in results)


def build_prompt(context: str, question: str) -> str:
    """Fill the two placeholders in a single pass, so user text is never re-interpreted."""
    values = {CONTEXT_PLACEHOLDER: context, QUESTION_PLACEHOLDER: question}
    return PLACEHOLDER_PATTERN.sub(lambda match: values[match.group(0)], PROMPT_TEMPLATE)


def clean_markdown(answer: str) -> str:
    """Remove Markdown formatting for plain terminal display; the wording is kept unchanged."""
    text = MARKDOWN_BOLD_PATTERN.sub(lambda match: match.group(1) or match.group(2), answer)
    text = MARKDOWN_BULLET_PATTERN.sub(r"\1- ", text)
    text = MARKDOWN_ITALIC_PATTERN.sub(r"\1", text)
    text = MARKDOWN_HEADING_PATTERN.sub("", text)
    return EXTRA_BLANK_LINES_PATTERN.sub("\n\n", text).strip()


def normalize_answer(answer: str) -> str:
    """Return the exact fallback phrase when the answer is only a formatting variation of it."""
    candidate = ANSWER_LABEL_PATTERN.sub("", answer.strip())
    candidate = candidate.strip().strip(QUOTES).strip().removesuffix(".").strip()
    if candidate.casefold() == FALLBACK_ANSWER.removesuffix(".").casefold():
        return FALLBACK_ANSWER
    return answer.strip()


class DocumentSearch:
    """Answers questions using only the chunks stored by the ingestion."""

    def __init__(self, settings: Settings):
        self._collection_name = settings.collection_name
        self._engine = create_engine(settings.database_url)
        embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model, google_api_key=settings.google_api_key
        )
        self._vector_store = PGVector(
            embeddings=embeddings,
            collection_name=settings.collection_name,
            connection=self._engine,
            use_jsonb=True,
        )
        # max_retries=1 means a single attempt; overload retries: OVERLOAD_WAITS_SECONDS.
        # No sampling parameters: gemini-3.5-flash-lite ignores them (deprecated by Google).
        self._llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key,
            max_retries=1,
        )

    def has_content(self) -> bool:
        return count_chunks(self._engine, self._collection_name) > 0

    def answer(self, question: str) -> str:
        return run_with_retries(
            lambda: self._answer_once(question),
            should_retry=is_server_error,
            waits=OVERLOAD_WAITS_SECONDS,
        )

    def _answer_once(self, question: str) -> str:
        results = self._vector_store.similarity_search_with_score(question, k=TOP_K)
        prompt = build_prompt(build_context(results), question)
        response = self._llm.invoke(prompt)
        return normalize_answer(clean_markdown(response.text))
