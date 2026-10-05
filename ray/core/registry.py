import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

DEFAULT_CONFIRM_PROMPT = "Точно выполнить команду?"


def normalize(text: str) -> str:
    """Приводит фразу к простому виду: строчные буквы, без знаков препинания."""
    text = text.lower().replace("ё", "е")
    cleaned = "".join(char if char.isalnum() or char.isspace() else " " for char in text)
    return " ".join(cleaned.split())


@dataclass(frozen=True)
class Command:
    name: str
    phrases: tuple[str, ...]
    handler: Callable[[], str | None]
    dangerous: bool = False
    confirm_prompt: str = DEFAULT_CONFIRM_PROMPT


@dataclass(frozen=True)
class PatternCommand:
    name: str
    pattern: re.Pattern
    handler: Callable[[re.Match], str | None]
    dangerous: bool = False
    confirm_prompt: str = DEFAULT_CONFIRM_PROMPT


class CommandRegistry:
    def __init__(self) -> None:
        self._commands_by_phrase: dict[str, Command] = {}
        self._pattern_commands: list[PatternCommand] = []

    def register(self, command: Command) -> None:
        for phrase in command.phrases:
            key = normalize(phrase)
            if key in self._commands_by_phrase:
                raise ValueError(f"Фраза уже занята другой командой: {phrase!r}")
            self._commands_by_phrase[key] = command

    def register_pattern(self, pattern_command: PatternCommand) -> None:
        self._pattern_commands.append(pattern_command)

    def find(self, text: str) -> Command | None:
        normalized = normalize(text)

        command = self._commands_by_phrase.get(normalized)
        if command is not None:
            return command

        for pattern_command in self._pattern_commands:
            match = pattern_command.pattern.fullmatch(normalized)
            if match:
                return Command(
                    name=pattern_command.name,
                    phrases=(),
                    handler=partial(pattern_command.handler, match),
                    dangerous=pattern_command.dangerous,
                    confirm_prompt=pattern_command.confirm_prompt,
                )
        return None


registry = CommandRegistry()


def command(
    *phrases: str,
    dangerous: bool = False,
    confirm_prompt: str = DEFAULT_CONFIRM_PROMPT,
):
    """Декоратор: команда с фиксированными фразами."""

    def decorator(handler: Callable[[], str | None]):
        registry.register(
            Command(handler.__name__, phrases, handler, dangerous, confirm_prompt)
        )
        return handler

    return decorator


def command_pattern(
    regex: str,
    dangerous: bool = False,
    confirm_prompt: str = DEFAULT_CONFIRM_PROMPT,
):
    """Декоратор: команда с параметром. Обработчик получает результат re.Match."""
    compiled = re.compile(regex)

    def decorator(handler: Callable[[re.Match], str | None]):
        registry.register_pattern(
            PatternCommand(handler.__name__, compiled, handler, dangerous, confirm_prompt)
        )
        return handler

    return decorator
