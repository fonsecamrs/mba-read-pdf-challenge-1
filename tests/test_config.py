import pytest

from config import ConfigError, load_settings

REQUIRED = {
    "GOOGLE_API_KEY": "test-key",
    "GOOGLE_EMBEDDING_MODEL": "embedding-model",
    "GOOGLE_LLM_MODEL": "llm-model",
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "postgres",
    "POSTGRES_DB": "rag",
}


def test_defaults_are_applied():
    settings = load_settings(REQUIRED)

    assert settings.llm_temperature == 0.0
    assert settings.postgres_host == "127.0.0.1"
    assert settings.postgres_port == 5432
    assert settings.collection_name == "document_chunks"
    assert settings.pdf_path == "document.pdf"
    assert settings.debug is False


@pytest.mark.parametrize("variable", sorted(REQUIRED))
def test_missing_required_variable_names_it(variable):
    environ = {**REQUIRED, variable: "  "}

    with pytest.raises(ConfigError) as error:
        load_settings(environ)

    assert error.value.code == "config.missing_variable"
    assert error.value.variable == variable
    assert variable in error.value.user_message


@pytest.mark.parametrize(
    ("variable", "value"),
    [("LLM_TEMPERATURE", "warm"), ("POSTGRES_PORT", "abc"), ("DEBUG", "maybe")],
)
def test_invalid_value_is_rejected(variable, value):
    with pytest.raises(ConfigError) as error:
        load_settings({**REQUIRED, variable: value})

    assert error.value.code == "config.invalid_variable"
    assert error.value.variable == variable


def test_database_url_escapes_credentials():
    settings = load_settings({**REQUIRED, "POSTGRES_PASSWORD": "p@ss:word"})

    assert settings.database_url == "postgresql+psycopg://postgres:p%40ss%3Aword@127.0.0.1:5432/rag"
