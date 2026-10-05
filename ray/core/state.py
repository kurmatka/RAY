from enum import Enum


class AssistantState(Enum):
    IDLE = "Ожидание"
    ACTIVATED = "Активация"
    LISTENING = "Слушаю"
    RECOGNIZING = "Распознаю"
    CONFIRMING = "Подтверждение"
    EXECUTING = "Выполняю"
    DONE = "Готов"
    ERROR = "Ошибка"
