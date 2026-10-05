import logging

from ray import commands  # noqa: F401
from ray.config import Config
from ray.core.command_processor import CommandProcessor
from ray.core.registry import registry
from ray.core.voice import VoiceRecognizer
from ray.logging_setup import setup_logging
from ray.core.tts import TextToSpeech


logger = logging.getLogger("ray")

MODEL_PATH = "models/vosk-model-small-ru-0.22"


def main() -> None:
    config = Config.load()
    setup_logging(config.log_level)
    logger.info("Рей запущен")

    processor = CommandProcessor(registry)
    recognizer = VoiceRecognizer(MODEL_PATH)
    speaker = TextToSpeech()

    print("Рей запущен.")
    print("Скажи «Рей», затем команду.")
    print("Для остановки нажми Ctrl+C.")

    while True:
        text = recognizer.listen_once()

        if text is None:
            continue

        print(f"[heard] {text}")

        text_lower = text.lower().strip()
        words = text_lower.split()

        if "рей" not in words and "рэй" not in words:
            continue

        print("[wake] Рей активирован!")

        # Если после слова "рей" уже была команда,
        # выполняем её сразу.
        command = text_lower

        if "рей" in words:
            index = words.index("рей")
            command = " ".join(words[index + 1:])

        elif "рэй" in words:
            index = words.index("рэй")
            command = " ".join(words[index + 1:])

        # В одной фразе было только "Рей" — ждём следующую команду.
        if not command:
            while True:
                print("[voice] Жду команду...")

                command = recognizer.listen_once(timeout=10)

                if command is None:
                    print("[dialog] Время ожидания истекло.")
                    break

                print(f"[command] {command}")

                command_lower = command.lower().strip()

                if command_lower in {
                    "выход",
                    "выйди",
                    "пока",
                    "спасибо",
                }:
                    print("[dialog] Возвращаюсь в режим ожидания.")
                    speaker.speak("Хорошо.")
                    break

                result = processor.process(command)
                print(f"[{result.status.value}] {result.message}")

                print("[tts] Говорю...")
                speaker.speak(result.message)
                print("[tts] Готово.")

            continue

        # Выполняем команду, которая была сказана сразу после "Рей".
        print(f"[command] {command}")

        result = processor.process(command)
        print(f"[{result.status.value}] {result.message}")

        print("[tts] Говорю...")
        speaker.speak(result.message)
        print("[tts] Готово.")


if __name__ == "__main__":
    main()