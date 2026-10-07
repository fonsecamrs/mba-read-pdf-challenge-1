"""Errors shown to the end user (Portuguese), with technical codes for debugging (English)."""

import logging
import sys
import time
import traceback
from collections.abc import Callable, Sequence

from google.genai.errors import ClientError, ServerError
from psycopg import OperationalError as PsycopgOperationalError
from sqlalchemy.exc import OperationalError as SqlAlchemyOperationalError

RATE_LIMIT_STATUS = 429
AUTH_FAILURE_STATUSES = {401, 403}
INVALID_API_KEY_MARKERS = ("API_KEY_INVALID", "API key not valid")


class AppError(Exception):
    """Error with a dot-notation `code` and a `user_message` shown to the end user."""

    def __init__(self, code: str, user_message: str):
        super().__init__(code)
        self.code = code
        self.user_message = user_message


def find_cause[E: BaseException](error: BaseException, error_type: type[E]) -> E | None:
    """Return the first exception of `error_type` in the chain of causes, if any."""
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        if isinstance(current, error_type):
            return current
        seen.add(id(current))
        current = current.__cause__ or current.__context__
    return None


def is_rate_limit_error(error: BaseException) -> bool:
    client_error = find_cause(error, ClientError)
    return client_error is not None and client_error.code == RATE_LIMIT_STATUS


def is_server_error(error: BaseException) -> bool:
    """Temporary failure on Google's side (5xx), e.g. 503 when the model is overloaded."""
    return find_cause(error, ServerError) is not None


def run_with_retries[T](
    operation: Callable[[], T],
    should_retry: Callable[[BaseException], bool],
    waits: Sequence[float],
    sleep: Callable[[float], None] = time.sleep,
    on_retry: Callable[[BaseException, float], None] | None = None,
) -> T:
    """Run `operation`, waiting `waits[i]` seconds before each new attempt on retryable errors."""
    for attempt in range(len(waits) + 1):
        try:
            return operation()
        except Exception as error:
            if attempt == len(waits) or not should_retry(error):
                raise
            if on_retry is not None:
                on_retry(error, waits[attempt])
            sleep(waits[attempt])
    raise AssertionError("unreachable")


def quiet_library_logs(debug: bool) -> None:
    """Hide library warnings unrelated to the user (e.g., google-genai AFC notices) unless debug."""
    if not debug:
        logging.getLogger("google_genai").setLevel(logging.ERROR)


def to_app_error(error: BaseException) -> AppError:
    """Translate any exception into the user-facing error it represents."""
    if isinstance(error, AppError):
        return error
    if is_rate_limit_error(error):
        return AppError(
            "llm.rate_limited",
            "O limite de uso da API do Gemini foi atingido. "
            "Aguarde alguns minutos e tente novamente.",
        )
    if is_server_error(error):
        return AppError(
            "llm.unavailable",
            "O serviço do Gemini está sobrecarregado no momento. Tente novamente em instantes.",
        )
    client_error = find_cause(error, ClientError)
    if client_error is not None and (
        client_error.code in AUTH_FAILURE_STATUSES
        or any(marker in str(client_error) for marker in INVALID_API_KEY_MARKERS)
    ):
        return AppError(
            "llm.auth_failed",
            "A API Key do Gemini é inválida ou não tem permissão de acesso.",
        )
    if find_cause(error, SqlAlchemyOperationalError) or find_cause(error, PsycopgOperationalError):
        return AppError(
            "database.unavailable",
            "Não foi possível conectar ao banco de dados. "
            "Verifique se o Docker está em execução (docker compose up -d).",
        )
    return AppError(
        "unexpected",
        "Ocorreu um erro inesperado. Execute novamente com DEBUG=true para ver os detalhes.",
    )


def report_error(error: BaseException, debug: bool) -> None:
    """Print the user message; with debug, also print the error code and the traceback."""
    app_error = to_app_error(error)
    print(app_error.user_message, file=sys.stderr)
    if debug:
        print(f"[{app_error.code}]", file=sys.stderr)
        traceback.print_exception(error, file=sys.stderr)
