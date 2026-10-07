import pytest
from google.genai.errors import ClientError
from langchain_google_genai._common import GoogleGenerativeAIError
from sqlalchemy.exc import OperationalError

from errors import AppError, is_rate_limit_error, to_app_error


def wrapped_client_error(code: int, message: str = "error") -> GoogleGenerativeAIError:
    """Simulate how langchain-google-genai wraps the Gemini SDK errors."""
    try:
        try:
            raise ClientError(code, {"error": {"message": message}})
        except ClientError as cause:
            raise GoogleGenerativeAIError("Error embedding content") from cause
    except GoogleGenerativeAIError as error:
        return error


def test_rate_limit_error_is_detected_through_the_wrapper():
    error = wrapped_client_error(429)

    assert is_rate_limit_error(error)
    assert to_app_error(error).code == "llm.rate_limited"


def test_other_client_errors_are_not_rate_limits():
    assert not is_rate_limit_error(wrapped_client_error(400))
    assert not is_rate_limit_error(ValueError("boom"))


@pytest.mark.parametrize(
    ("code", "message"),
    [(400, "API key not valid. Please pass a valid API key."), (403, "Permission denied")],
)
def test_auth_failures(code, message):
    assert to_app_error(wrapped_client_error(code, message)).code == "llm.auth_failed"


def test_database_unavailable_through_a_generic_wrapper():
    try:
        try:
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))
        except OperationalError as cause:
            raise Exception("Failed to create vector extension") from cause
    except Exception as error:
        assert to_app_error(error).code == "database.unavailable"


def test_app_error_is_kept_and_unknown_errors_are_unexpected():
    app_error = AppError("ingestion.pdf_not_found", "Arquivo PDF não encontrado: x.pdf")

    assert to_app_error(app_error) is app_error
    assert to_app_error(RuntimeError("boom")).code == "unexpected"
