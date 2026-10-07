"""PDF ingestion: load, split, embed and store the chunks in PostgreSQL with pgVector (spec 001)."""

import logging
import sys
import time
import warnings
from pathlib import Path

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import create_engine

from config import Settings, load_settings
from errors import (
    AppError,
    is_rate_limit_error,
    is_server_error,
    quiet_library_logs,
    report_error,
    run_with_retries,
)
from search import count_chunks

with warnings.catch_warnings():
    # langchain-community is sunset but kept on purpose (ADR-005): hide its import warning.
    warnings.filterwarnings(
        "ignore", message=".*langchain-community.*", category=DeprecationWarning
    )
    from langchain_community.document_loaders import PyPDFLoader

# Fixed by the challenge (FR-002)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Texts sent per embeddings request. Free tier limits for gemini-embedding-2 are 100 RPM
# (each text appears to count as one request) and 30K TPM; 50 texts stay below both (DF-03).
EMBEDDING_BATCH_SIZE = 50

# Waits before each new attempt when Gemini reports a usage limit or overload (NFR-005, DF-03).
# Limits are per minute, so the waits add up to more than one minute.
RATE_LIMIT_WAITS_SECONDS = (30, 60, 60)

# Metadata kept for each chunk (DATA-001)
KEPT_METADATA = ("source", "page")

YES_ANSWERS = {"s", "sim"}
NO_ANSWERS = {"n", "nao", "não"}

logger = logging.getLogger(__name__)


def build_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)


def parse_confirmation(answer: str) -> bool | None:
    """Return True for yes, False for no, None for any other answer."""
    normalized = answer.strip().lower()
    if normalized in YES_ANSWERS:
        return True
    if normalized in NO_ANSWERS:
        return False
    return None


def load_pages(pdf_path: str) -> list[Document]:
    if not Path(pdf_path).is_file():
        raise AppError("ingestion.pdf_not_found", f"Arquivo PDF não encontrado: {pdf_path}")
    pages = PyPDFLoader(pdf_path).load()
    if not any(page.page_content.strip() for page in pages):
        raise AppError(
            "ingestion.pdf_no_text",
            "Não foi possível extrair texto do PDF. Verifique se ele não é um documento escaneado.",
        )
    return pages


def split_pages(pages: list[Document]) -> list[Document]:
    chunks = build_text_splitter().split_documents(pages)
    for chunk in chunks:
        chunk.metadata = {
            key: chunk.metadata[key] for key in KEPT_METADATA if key in chunk.metadata
        }
    return chunks


def confirm_replacement() -> bool:
    while True:
        try:
            answer = input("Já existe um documento ingerido na base. Deseja substituí-lo? (s/n): ")
        except (KeyboardInterrupt, EOFError):
            print()
            return False
        confirmed = parse_confirmation(answer)
        if confirmed is not None:
            return confirmed


def embed_with_retry(
    embeddings: GoogleGenerativeAIEmbeddings,
    texts: list[str],
    waits: tuple[int, ...] = RATE_LIMIT_WAITS_SECONDS,
    sleep=time.sleep,
) -> list[list[float]]:
    """Embed the texts in batches, retrying a batch on usage limits or Gemini overload."""
    vectors: list[list[float]] = []
    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start : start + EMBEDDING_BATCH_SIZE]
        vectors.extend(
            run_with_retries(
                lambda batch=batch: embeddings.embed_documents(batch),
                should_retry=is_retryable,
                waits=waits,
                sleep=sleep,
                on_retry=announce_retry,
            )
        )
    return vectors


def is_retryable(error: BaseException) -> bool:
    return is_rate_limit_error(error) or is_server_error(error)


def announce_retry(error: BaseException, wait: float) -> None:
    reason = (
        "Limite de uso da API do Gemini atingido."
        if is_rate_limit_error(error)
        else "O serviço do Gemini está sobrecarregado."
    )
    print(f"{reason} Nova tentativa em {wait:g} segundos...")


def replace_content(vector_store: PGVector, chunks: list[Document], vectors: list[list[float]]):
    vector_store.delete_collection()
    vector_store.create_collection()
    vector_store.add_embeddings(
        texts=[chunk.page_content for chunk in chunks],
        embeddings=vectors,
        metadatas=[chunk.metadata for chunk in chunks],
    )


def ingest(settings: Settings) -> None:
    pages = load_pages(settings.pdf_path)
    chunks = split_pages(pages)
    logger.info("Loaded %d pages, split into %d chunks", len(pages), len(chunks))

    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model, google_api_key=settings.google_api_key
    )
    engine = create_engine(settings.database_url)
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=settings.collection_name,
        connection=engine,
        use_jsonb=True,
    )

    if count_chunks(engine, settings.collection_name) > 0 and not confirm_replacement():
        print("Ingestão cancelada. Nenhum dado foi alterado.")
        return

    # Embed before removing the old content, so a Gemini failure keeps it intact (ADR-003)
    vectors = embed_with_retry(embeddings, [chunk.page_content for chunk in chunks])
    replace_content(vector_store, chunks, vectors)
    print(f"Ingestão concluída: {len(chunks)} trechos gravados a partir de {len(pages)} páginas.")


def main() -> int:
    debug = False
    try:
        settings = load_settings()
        debug = settings.debug
        if debug:
            logging.basicConfig(level=logging.INFO)
        quiet_library_logs(debug)
        ingest(settings)
        return 0
    except KeyboardInterrupt:
        print("\nIngestão interrompida.")
        return 1
    except Exception as error:
        report_error(error, debug)
        return 1


if __name__ == "__main__":
    sys.exit(main())
