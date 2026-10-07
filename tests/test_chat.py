import pytest

from chat import chat_loop, is_exit_command
from errors import AppError


def scripted_input(*lines):
    """Simulate typed lines; raises EOFError when they run out (like Ctrl+D / Ctrl+Z)."""
    remaining = list(lines)

    def read(_prompt):
        if not remaining:
            raise EOFError
        line = remaining.pop(0)
        if isinstance(line, BaseException):
            raise line
        return line

    return read


@pytest.mark.parametrize("text", ["sair", " SAIR ", "Sair"])
def test_exit_command(text):
    assert is_exit_command(text)


@pytest.mark.parametrize("text", ["sair agora", "", "sai"])
def test_not_exit_command(text):
    assert not is_exit_command(text)


def test_loop_answers_until_exit(capsys):
    questions = []

    def answer(question):
        questions.append(question)
        return "O faturamento foi de 10 milhões de reais."

    chat_loop(answer, debug=False, read=scripted_input("Qual o faturamento?", "sair"))

    output = capsys.readouterr().out
    assert questions == ["Qual o faturamento?"]
    assert output.startswith("Faça sua pergunta:\n\n")
    assert "RESPOSTA: O faturamento foi de 10 milhões de reais.\n" in output
    assert output.endswith("Até logo!\n")


def test_empty_input_never_calls_the_api():
    questions = []

    chat_loop(questions.append, debug=False, read=scripted_input("", "   ", "sair"))

    assert questions == []


@pytest.mark.parametrize("interruption", [KeyboardInterrupt(), EOFError()])
def test_interruption_says_goodbye(capsys, interruption):
    chat_loop(lambda _q: "x", debug=False, read=scripted_input(interruption))

    assert capsys.readouterr().out.endswith("Até logo!\n")


def test_error_during_a_question_keeps_the_chat_running(capsys):
    calls = []

    def answer(question):
        calls.append(question)
        if len(calls) == 1:
            raise AppError("llm.rate_limited", "O limite de uso da API do Gemini foi atingido.")
        return "ok"

    chat_loop(answer, debug=False, read=scripted_input("primeira", "segunda", "sair"))

    captured = capsys.readouterr()
    assert "O limite de uso da API do Gemini foi atingido." in captured.err
    assert "RESPOSTA: ok" in captured.out
    assert calls == ["primeira", "segunda"]
