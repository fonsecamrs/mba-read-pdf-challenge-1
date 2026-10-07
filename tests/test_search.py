import re
from pathlib import Path

import pytest
from langchain_core.documents import Document

from search import (
    FALLBACK_ANSWER,
    PROMPT_TEMPLATE,
    build_context,
    build_prompt,
    clean_markdown,
    normalize_answer,
)

CLAUDE_MD = Path(__file__).resolve().parents[1] / "CLAUDE.md"


def canonical_prompt() -> str:
    """The prompt block that CLAUDE.md declares as canonical."""
    content = CLAUDE_MD.read_text(encoding="utf-8")
    match = re.search(r"Use este prompt sem alterar o texto.*?```text\n(.*?)\n```", content, re.S)
    assert match, "canonical prompt block not found in CLAUDE.md"
    return match.group(1)


def test_template_matches_the_canonical_prompt():
    assert PROMPT_TEMPLATE == canonical_prompt()


def test_context_joins_chunks_in_order_with_a_blank_line():
    results = [
        (Document(page_content="primeiro", metadata={"page": 2}), 0.1),
        (Document(page_content="segundo", metadata={"page": 0}), 0.3),
    ]

    assert build_context(results) == "primeiro\n\nsegundo"


def test_prompt_replaces_only_the_two_placeholders():
    prompt = build_prompt("CTX", "Qual o faturamento?")

    expected = PROMPT_TEMPLATE.replace(
        "{resultados concatenados do banco de dados}", "CTX"
    ).replace("{pergunta do usuário}", "Qual o faturamento?")
    assert prompt == expected


def test_user_text_is_inserted_literally():
    question = "E se eu digitar {pergunta do usuário} ou {x}?"
    context = "trecho com {resultados concatenados do banco de dados}"

    prompt = build_prompt(context, question)

    assert f"CONTEXTO:\n{context}\n" in prompt
    assert f"PERGUNTA DO USUÁRIO:\n{question}\n" in prompt


@pytest.mark.parametrize(
    "answer",
    [
        FALLBACK_ANSWER,
        f'"{FALLBACK_ANSWER}"',
        f"“{FALLBACK_ANSWER}”",
        FALLBACK_ANSWER.removesuffix("."),
        f"  {FALLBACK_ANSWER}  \n",
        f'Resposta: "{FALLBACK_ANSWER}"',
        "não tenho informações necessárias para responder sua pergunta",
    ],
)
def test_fallback_variations_become_the_exact_phrase(answer):
    assert normalize_answer(answer) == FALLBACK_ANSWER


@pytest.mark.parametrize(
    "answer",
    [
        "O faturamento foi de 10 milhões de reais.",
        f"{FALLBACK_ANSWER} Porém, o faturamento foi de 10 milhões de reais.",
    ],
)
def test_other_answers_are_kept(answer):
    assert normalize_answer(answer) == answer


def test_markdown_is_removed_without_changing_the_wording():
    answer = (
        "Com base no contexto, os CEOs foram:\n\n\n"
        "1. **Henrique Valadares Moura** - 2005-2014\n"
        "* **2021:** R$ 102,5 milhões\n"
        "  + item __interno__\n"
        "## Resumo\n"
        "Vigente. *(Nota: renovada em 2025).*\n"
        "Fim.\n\n"
    )

    assert clean_markdown(answer) == (
        "Com base no contexto, os CEOs foram:\n\n"
        "1. Henrique Valadares Moura - 2005-2014\n"
        "- 2021: R$ 102,5 milhões\n"
        "  - item interno\n"
        "Resumo\n"
        "Vigente. (Nota: renovada em 2025).\n"
        "Fim."
    )


def test_plain_answers_are_kept_by_clean_markdown():
    answer = "A receita de 2025 foi de R$ 192,4 milhões (3 * 2 = 6 não é afetado)."

    assert clean_markdown(answer) == answer


def test_bold_fallback_phrase_is_still_normalized():
    assert normalize_answer(clean_markdown(f"**{FALLBACK_ANSWER}**")) == FALLBACK_ANSWER
