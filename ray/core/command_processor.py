import logging
from dataclasses import dataclass
from enum import Enum
from difflib import SequenceMatcher

from ray.core.registry import CommandRegistry, normalize


logger = logging.getLogger("ray.core.command_processor")


class CommandStatus(Enum):
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    ERROR = "error"
    CONFIRMATION = "confirmation"


@dataclass
class CommandResult:
    status: CommandStatus
    message: str


class CommandProcessor:
    def __init__(self, registry: CommandRegistry):
        self.registry = registry

    def _fuzzy_find(self, text: str):
        normalized = normalize(text)

        if not normalized:
            return None

        words = normalized.split()

        if len(words) < 2:
            return None

        best_command = None
        best_score = 0.0

        for phrase, command in self.registry._commands_by_phrase.items():
            phrase_words = phrase.split()

            if abs(len(words) - len(phrase_words)) > 1:
                continue

            # ====================================================
            # Vosk пропустил одно слово
            #
            # "крой калькулятор"
            #       ↓
            # "открой калькулятор"
            # ====================================================

            if len(phrase_words) == len(words) + 1:
                for skip_index in range(len(phrase_words)):
                    shortened = (
                        phrase_words[:skip_index]
                        + phrase_words[skip_index + 1:]
                    )

                    scores = [
                        SequenceMatcher(None, a, b).ratio()
                        for a, b in zip(words, shortened)
                    ]

                    score = sum(scores) / len(scores)

                    if score > best_score:
                        best_score = score
                        best_command = command

            # ====================================================
            # Обычное сравнение слово к слову
            # ====================================================

            elif len(phrase_words) == len(words):
                scores = [
                    SequenceMatcher(None, a, b).ratio()
                    for a, b in zip(words, phrase_words)
                ]

                score = sum(scores) / len(scores)

                if score > best_score:
                    best_score = score
                    best_command = command

        # ========================================================
        # Безопасный порог
        # ========================================================

        if best_command is not None and best_score >= 0.75:
            logger.info(
                "Fuzzy: %r -> %s (%.2f)",
                text,
                best_command.name,
                best_score,
            )

            return best_command

        return None

    def process(self, text: str) -> CommandResult:
        text = text.strip()

        if not text:
            return CommandResult(
                CommandStatus.NOT_FOUND,
                "Я не понял команду",
            )

        # ========================================================
        # 1. Сначала точное совпадение
        # ========================================================

        command = self.registry.find(text)

        # ========================================================
        # 2. Если точного нет — осторожный fuzzy
        # ========================================================

        if command is None:
            command = self._fuzzy_find(text)

        # ========================================================
        # 3. Команда вообще не найдена
        # ========================================================

        if command is None:
            logger.info(
                "Команда не найдена: %r",
                text,
            )

            return CommandResult(
                CommandStatus.NOT_FOUND,
                "Я не понял команду",
            )

        # ========================================================
        # 4. Опасная команда
        # ========================================================

        if command.dangerous:
            return CommandResult(
                CommandStatus.CONFIRMATION,
                command.confirm_prompt,
            )

        # ========================================================
        # 5. Выполнение команды
        # ========================================================

        try:
            message = command.handler()

            if message is None:
                message = "Готово"

            return CommandResult(
                CommandStatus.SUCCESS,
                message,
            )

        except Exception:
            logger.exception(
                "Ошибка выполнения команды: %r",
                text,
            )

            return CommandResult(
                CommandStatus.ERROR,
                "При выполнении команды произошла ошибка",
            )