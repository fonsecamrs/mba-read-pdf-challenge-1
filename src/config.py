"""Settings shared by the ingestion and chat scripts, read from environment variables (.env)."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import quote_plus

from dotenv import load_dotenv

from errors import AppError

# Fail fast instead of hanging when the database is unreachable
CONNECT_TIMEOUT_SECONDS = 10

REQUIRED_VARIABLES = (
    "GOOGLE_API_KEY",
    "GOOGLE_EMBEDDING_MODEL",
    "GOOGLE_LLM_MODEL",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
)

DEFAULTS = {
    "LLM_TEMPERATURE": "0",
    "POSTGRES_HOST": "127.0.0.1",
    "POSTGRES_PORT": "5432",
    "PG_VECTOR_COLLECTION_NAME": "document_chunks",
    "PDF_PATH": "document.pdf",
    "DEBUG": "false",
}

TRUE_VALUES = {"true", "1", "yes"}
FALSE_VALUES = {"false", "0", "no"}


class ConfigError(AppError):
    """Invalid or missing configuration variable."""

    def __init__(self, code: str, variable: str, user_message: str):
        super().__init__(code, user_message)
        self.variable = variable


@dataclass(frozen=True)
class Settings:
    google_api_key: str
    embedding_model: str
    llm_model: str
    llm_temperature: float
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    collection_name: str
    pdf_path: str
    debug: bool

    @property
    def database_url(self) -> str:
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql+psycopg://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            f"?connect_timeout={CONNECT_TIMEOUT_SECONDS}"
        )


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Build the settings from `environ`, or from `.env` and the process environment."""
    if environ is None:
        load_dotenv()
        environ = os.environ

    values = {name: environ.get(name, "").strip() for name in REQUIRED_VARIABLES}
    for name, value in values.items():
        if not value:
            raise ConfigError(
                "config.missing_variable",
                name,
                f"A variável {name} não está configurada no arquivo .env.",
            )
    for name, default in DEFAULTS.items():
        values[name] = environ.get(name, "").strip() or default

    return Settings(
        google_api_key=values["GOOGLE_API_KEY"],
        embedding_model=values["GOOGLE_EMBEDDING_MODEL"],
        llm_model=values["GOOGLE_LLM_MODEL"],
        llm_temperature=_parse_float("LLM_TEMPERATURE", values["LLM_TEMPERATURE"]),
        postgres_user=values["POSTGRES_USER"],
        postgres_password=values["POSTGRES_PASSWORD"],
        postgres_db=values["POSTGRES_DB"],
        postgres_host=values["POSTGRES_HOST"],
        postgres_port=_parse_int("POSTGRES_PORT", values["POSTGRES_PORT"]),
        collection_name=values["PG_VECTOR_COLLECTION_NAME"],
        pdf_path=values["PDF_PATH"],
        debug=_parse_bool("DEBUG", values["DEBUG"]),
    )


def _invalid(name: str) -> ConfigError:
    return ConfigError(
        "config.invalid_variable",
        name,
        f"A variável {name} tem um valor inválido no arquivo .env.",
    )


def _parse_float(name: str, value: str) -> float:
    try:
        return float(value)
    except ValueError:
        raise _invalid(name) from None


def _parse_int(name: str, value: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise _invalid(name) from None


def _parse_bool(name: str, value: str) -> bool:
    lowered = value.lower()
    if lowered in TRUE_VALUES:
        return True
    if lowered in FALSE_VALUES:
        return False
    raise _invalid(name)
