from ray.core.voice import VoiceRecognizer

MODEL_PATH = "models/vosk-model-small-ru-0.22"

recognizer = VoiceRecognizer(MODEL_PATH)

print("Тест микрофона.")
print("Скажи несколько слов после сообщения '[voice] Слушаю...'")
print("Для остановки нажми Ctrl+C.")

while True:
    text = recognizer.listen_once()
    print(f"[recognized] {text}")
