import pytest
from google.genai.errors import ClientError, ServerError
from langchain_core.documents import Document

from errors import AppError
from ingest import (
    build_text_splitter,
    embed_with_retry,
    load_pages,
    parse_confirmation,
    split_pages,
)


class FakeEmbeddings:
    """Raises the given errors call by call (None = success), then returns one vector per text."""

    def __init__(self, errors=()):
        self.errors = list(errors)
        self.calls = []

    def embed_documents(self, texts):
        self.calls.append(list(texts))
        error = self.errors.pop(0) if self.errors else None
        if error is not None:
            raise error
        return [[float(len(text))] for text in texts]


def rate_limit_error():
    return ClientError(429, {"error": {"message": "Resource exhausted"}})


def test_splitter_uses_challenge_chunk_size_and_overlap():
    splitter = build_text_splitter()

    assert splitter._chunk_size == 1000
    assert splitter._chunk_overlap == 150


@pytest.mark.parametrize("answer", ["s", "S", " sim ", "SIM"])
def test_confirmation_yes(answer):
    assert parse_confirmation(answer) is True


@pytest.mark.parametrize("answer", ["n", "N", "não", "NAO", " nao "])
def test_confirmation_no(answer):
    assert parse_confirmation(answer) is False


@pytest.mark.parametrize("answer", ["", "x", "talvez", "yes"])
def test_confirmation_invalid(answer):
    assert parse_confirmation(answer) is None


def test_missing_pdf_raises_pdf_not_found(tmp_path):
    with pytest.raises(AppError) as error:
        load_pages(str(tmp_path / "missing.pdf"))

    assert error.value.code == "ingestion.pdf_not_found"


def test_split_keeps_only_source_and_page_metadata():
    page = Document(
        page_content="texto " * 400,
        metadata={"source": "document.pdf", "page": 0, "producer": "x", "total_pages": 3},
    )

    chunks = split_pages([page])

    assert len(chunks) > 1
    assert all(len(chunk.page_content) <= 1000 for chunk in chunks)
    assert all(chunk.metadata == {"source": "document.pdf", "page": 0} for chunk in chunks)


def test_embed_retries_after_rate_limit():
    embeddings = FakeEmbeddings(errors=[rate_limit_error(), rate_limit_error()])
    sleeps = []

    vectors = embed_with_retry(embeddings, ["a", "bb"], waits=(1, 2, 3), sleep=sleeps.append)

    assert vectors == [[1.0], [2.0]]
    assert sleeps == [1, 2]


def test_embed_gives_up_after_all_waits():
    embeddings = FakeEmbeddings(errors=[rate_limit_error()] * 3)
    sleeps = []

    with pytest.raises(ClientError):
        embed_with_retry(embeddings, ["a"], waits=(1, 2), sleep=sleeps.append)

    assert sleeps == [1, 2]


def test_embed_does_not_retry_other_errors():
    embeddings = FakeEmbeddings(errors=[ValueError("boom")])
    sleeps = []

    with pytest.raises(ValueError):
        embed_with_retry(embeddings, ["a"], waits=(1, 2), sleep=sleeps.append)

    assert sleeps == []
    assert len(embeddings.calls) == 1


def test_embed_sends_batches_of_50():
    embeddings = FakeEmbeddings()

    vectors = embed_with_retry(embeddings, ["x"] * 120, waits=(), sleep=lambda _: None)

    assert [len(call) for call in embeddings.calls] == [50, 50, 20]
    assert len(vectors) == 120


def test_only_the_failed_batch_is_retried():
    embeddings = FakeEmbeddings(errors=[None, rate_limit_error()])

    vectors = embed_with_retry(embeddings, ["x"] * 60, waits=(1,), sleep=lambda _: None)

    assert [len(call) for call in embeddings.calls] == [50, 10, 10]
    assert len(vectors) == 60


def test_embed_retries_when_gemini_is_overloaded(capsys):
    overloaded = ServerError(503, {"error": {"message": "high demand"}})
    embeddings = FakeEmbeddings(errors=[overloaded])
    sleeps = []

    vectors = embed_with_retry(embeddings, ["a"], waits=(30,), sleep=sleeps.append)

    assert vectors == [[1.0]]
    assert sleeps == [30]
    assert "sobrecarregado. Nova tentativa em 30 segundos" in capsys.readouterr().out
