"""Terminal chat: asks questions about the ingested PDF (spec 002)."""

import logging
import sys
from collections.abc import Callable

from config import load_settings
from errors import AppError, quiet_library_logs, report_error
from search import DocumentSearch

EXIT_COMMAND = "sair"
FAREWELL = "Até logo!"


def is_exit_command(text: str) -> bool:
    return text.strip().casefold() == EXIT_COMMAND


def read_question(read: Callable[[str], str]) -> str:
    """Ask until a non-empty question is typed; empty input never reaches the API (FR-010)."""
    while True:
        question = read("PERGUNTA: ").strip()
        if question:
            return question


def chat_loop(
    answer: Callable[[str], str],
    debug: bool,
    read: Callable[[str], str] = input,
) -> None:
    """Question loop until `sair`, Ctrl+C or end of input (FR-009)."""
    try:
        while True:
            print("Faça sua pergunta:")
            print()
            question = read_question(read)
            if is_exit_command(question):
                break
            try:
                print(f"RESPOSTA: {answer(question)}")
            except Exception as error:
                # Errors during a question do not end the chat (spec 002, section 9)
                report_error(error, debug)
            print()
    except (KeyboardInterrupt, EOFError):
        print()
    print(FAREWELL)


def main() -> int:
    debug = False
    try:
        settings = load_settings()
        debug = settings.debug
        if debug:
            logging.basicConfig(level=logging.INFO)
        quiet_library_logs(debug)
        search = DocumentSearch(settings)
        if not search.has_content():
            raise AppError(
                "chat.no_content",
                "Nenhum documento foi ingerido. Execute primeiro: python src/ingest.py",
            )
    except KeyboardInterrupt:
        print(f"\n{FAREWELL}")
        return 0
    except Exception as error:
        report_error(error, debug)
        return 1

    chat_loop(search.answer, debug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
